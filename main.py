from flask import Flask, render_template, request, redirect, url_for, session, make_response
from test import con_my_sql
from datetime import timedelta
from flask import request, jsonify
import os
from ultralytics import YOLO
import time
import glob
import json
from test import get_user_id
# 在现有导入部分添加
import pymysql  # 新增
import re       # 新增
from weasyprint import HTML
import tempfile
from datetime import datetime
from urllib.parse import quote
app = Flask(
    __name__,
    static_folder='/root/myweb/static',      # 指定静态文件夹路径
    static_url_path='/static'    # 设置静态资源URL前缀
)


@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(e):
    return jsonify({
        "error": e.description if hasattr(e, 'description') else str(e)
    }), e.code if hasattr(e, 'code') else 500
# ---------------------- 数据迁移函数 ----------------------
def migrate_image_paths():
    """自动修复数据库中的图片路径为 Web 可访问路径"""
    conn = None  # 初始化 conn 为 None
    try:
        # 数据库配置（需与你的实际配置一致）
        db_config = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "123456",
            "database": "demo01",
            "charset": "utf8mb4"
        }

        # 连接数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # 查询所有历史记录
        cursor.execute("SELECT id, image_path FROM user_history")
        records = cursor.fetchall()

        # 遍历修复路径
        updated_count = 0
        for record in records:
            record_id, old_path = record
            # 匹配 static/results/... 部分
            match = re.search(r'(static[\\/]results[\\/].+?\.jpg)', old_path, re.IGNORECASE)
            if match:
                new_path = '/' + match.group(1).replace('\\', '/')
                # 修复括号未闭合错误
                cursor.execute(
                    "UPDATE user_history SET image_path = %s WHERE id = %s",  # 添加闭合括号
                    (new_path, record_id)
                )
                updated_count += 1

        # 提交事务（移动到循环外）
        conn.commit()
        print(f"[数据库迁移] 成功修复 {updated_count} 条图片路径")

    except pymysql.MySQLError as e:
        print(f"[数据库迁移错误] 操作失败: {str(e)}")
        conn.rollback()
    finally:
        if conn:
            conn.close()
app.secret_key = 'your_secret_key'  # 设置会话密钥
# 设置会话有效期为1天
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # 每次请求刷新会话时间
@app.route("/")
def index():
    return render_template('homepage.html')



UPLOAD_FOLDER = '/root/myweb/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # 获取上传的文件
        files = request.files
        if not files:
            return jsonify({'error': 'No files uploaded'}), 400

        # 保存所有文件
        saved_files = []
        for key in files:
            file = files[key]
            if file.filename == '':
                continue
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            saved_files.append(filename)

        return jsonify({
            'message': f'{len(saved_files)} files uploaded successfully',
            'files': saved_files
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/use")
def index_use():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('use.html')

# 跳转
@app.route("/contact")
def index_contact():
    return render_template('contact.html')

@app.route("/index")
def index_index():
    # return render_template('index.html')
    if 'username' in session:
        return redirect(url_for('index_use'))
    return render_template('index.html')  # 显示登录页面


@app.route('/introduce')
def index_introduce():
    return render_template('introduce.html')
@app.route("/scheme")
def index_scheme():
    return render_template('scheme.html')

@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("username")
    pwd = request.form.get("password")

    code = "select * from login_user where username ='%s'" % (name)
    cursor_ans = con_my_sql(code)
    cursor_select = cursor_ans.fetchall()

    if len(cursor_select) > 0 and pwd == cursor_select[0]['password']:
        session.permanent = True
        session['username'] = name  # 存储用户会话信息
        return redirect(url_for("index_use"))
    else:
        return redirect(url_for("login"))
    return redirect(url_for("index.html"))
@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("username")
    pwd = request.form.get("password")
    pwd2 = request.form.get("password2")

    # 检查两次输入的密码是否一致
    if pwd != pwd2:
        return redirect(url_for("index_index"))
    code = "select * from login_user where username ='%s'" % (name)
    cursor_ans = con_my_sql(code)
    cursor_select = cursor_ans.fetchall()
    if len(cursor_select) > 0:
        return redirect(url_for("index_index"))
    else:
        code = "INSERT INTO `login_user`(`username`,`password`) VALUES ('%s', '%s')" % (name, pwd)
        con_my_sql(code)
        return redirect(url_for("index_index"))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


# 加载预训练模型
model = YOLO(r"/root/myweb/best.pt")
print(f"模型加载状态: {model is not None}") 

@app.route('/get_history')
def get_history():
    try:
        username = session.get('username')
        if not username:
            return jsonify({'error': 'Not logged in'}), 401

        user_id = get_user_id(username)
        # 原有代码：定义SQL查询
        code = f"""
        SELECT image_path, analysis_results, created_at, total_areas  -- 新增 total_areas
        FROM user_history
        WHERE user_id = {user_id}
        ORDER BY created_at DESC
        LIMIT 5
        """
        cursor = con_my_sql(code)
        history = cursor.fetchall()
        print("[DEBUG] History data:", history)
        return jsonify(history), 200

    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        username = session.get('username')
        if not username:
            return jsonify({'error': '未登录'}), 401

        data = request.json
        original_image = url_for('static', filename=data.get('original_image').replace('static/', '',1), _external=True)
        analyzed_image = url_for('static', filename=data.get('analyzed_image').replace('static/', '',1), _external=True)

        # 生成医疗建议
        def generate_advice(lesion_type, area):
            area = float(area)
            if lesion_type == "IRF":
                if area < 3440:
                    return "Regular observation (OCT review every 3-6 months), no treatment required for now. It is recommended to control systemic risk factors (such as hypertension, high cholesterol), and supplement with antioxidants like lutein and zeaxanthin."
                elif 3440 <= area <= 9000:
                    return "Close follow-up (OCT review every 1-2 months). If there is continued growth or accompanied by vision decline, initiate anti-VEGF treatment (such as ranibizumab or aflibercept), with a loading dose of 3 injections followed by treatment as needed."
                else:
                    return "Urgent treatment required! Immediately initiate anti-VEGF injections (once monthly for 3 consecutive doses), combined with OCT angiography (OCTA) to screen for CNV. If accompanied by SRF or PED, the follow-up interval should be shortened to 2-4 weeks."
            elif lesion_type == "SRF":
                if area < 489:
                    return "Monitor and observe the central macular thickness (CMT); if asymptomatic, treatment may be temporarily withheld. It is recommended to avoid strenuous activities to prevent fluid diffusion."
                elif 489 <= area <= 1000:
                    return "Anti-VEGF treatment (once every 4-6 weeks), combined with photodynamic therapy (PDT) if classic CNV is present. It is recommended to review OCT monthly to assess fluid absorption."
                else:
                    return "Urgent intervention required! Anti-VEGF combined with PDT, or consider intravitreal corticosteroid injection (such as triamcinolone acetonide). If the fovea is involved, referral to a retinal specialist within 24 hours is necessary."
            elif lesion_type == "SHRM":
                if area < 3000:
                    return "Observation, possibly due to old hemorrhage or fibrosis. It is recommended to screen for systemic coagulation dysfunction and avoid the misuse of anticoagulant medications."
                elif 3000 <= area <= 6000:
                    return "Combine with fluorescein angiography (FFA) to determine active bleeding. If CNV is present, initiate anti-VEGF treatment. If it is a fibrotic scar, consider long-term observation."
                else:
                    return "Multidisciplinary consultation required! Combined anti-VEGF, PDT, and surgery (such as vitrectomy) may be needed to clear extensive bleeding. It is recommended to review OCTA within 2 weeks to assess CNV activity."
            elif lesion_type == "PED":
                if area < 3000:
                    return "Observation, possibly serous PED. It is recommended to avoid strong light exposure and take vitamin supplements orally."
                elif 3000 <= area <= 6000:
                    return "Anti-VEGF treatment (once every 4 weeks); if it is serous PED, laser photocoagulation to seal the leakage point can be attempted. Fibrovascular PED requires combination with PDT."
                else:
                    return "Urgent intervention required! Anti-VEGF combined with micropulse laser, or intravitreal injection of anti-inflammatory drugs. If there is a high risk of PED rupture, surgical intervention within 72 hours is necessary."
            return "No specific recommendations."

        # advice = {lesion: generate_advice(lesion, area) for lesion, area in analysis_data['areas'].items()}
        advice = {lesion: generate_advice(lesion, area) for lesion, area in data.get('areas').items()}
        # 渲染HTML模板
        # current_time = datetime.now()  # 获取当前时间
        # html = render_template(
        #     'report_template.html',
        #     **analysis_data,
        #     advice=advice,
        #     current_time=current_time  # 传递当前时间到模板
        # )
        html = render_template(
            'report_template.html',
            original_image=original_image,
            analyzed_image=analyzed_image,
            areas=data.get('areas'),
            advice=advice,
            current_time=datetime.now()
        )

        # 生成PDF
        pdf = HTML(string=html).write_pdf()

        # 返回PDF文件
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        filename = f'检测报告_{int(time.time())}.pdf'
        encoded_filename = quote(filename, encoding='utf-8')
        response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf)
            print(f"[DEBUG] PDF临时文件路径：{tmp.name}")

        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not logged in'}), 401

        user_id = get_user_id(username)
        if not user_id:
            return jsonify({'error': 'User not found'}), 404

        # 获取图片路径（需确保前端传递此参数）
        data = request.json
        image_path = data.get('image_path')
        if not image_path:
            return jsonify({'error': 'Missing image_path parameter'}), 400
        print(image_path)
        # 模型推理
        results = model(image_path, save=True)
        print(results)
        # ---------- 关键修复：生成 analysis_result ----------
        analysis_result = []  # 显式初始化
        total_areas = {}
        classlist = {0: 'PED', 1: 'SRF', 2: 'IS/OS', 3: 'SHRM', 4: 'IRF'}
        for r in results:
            if hasattr(r, 'boxes') and r.boxes is not None:
                cls = r.boxes.cls.tolist()
                box = r.boxes.xyxy.tolist()
                for i in range(len(cls)):
                    class_name = classlist.get(int(cls[i]), 'Unknown')
                    if i < len(box):
                        x1, y1, x2, y2 = box[i]
                        area = (x2 - x1) * (y2 - y1)
                    else:
                        area = 0
                    total_areas[class_name] = total_areas.get(class_name, 0) + area
        total_areas_json = json.dumps(total_areas)
        for r in results:
            # 确保模型返回的检测结果有效
            if hasattr(r, 'boxes') and r.boxes is not None:
                cls = r.boxes.cls.tolist()
                box = r.boxes.xyxy.tolist()
                for i in range(len(cls)):
                    # 添加类别和边界框数据
                    analysis_result.append({
                        'class': classlist.get(int(cls[i]), 'Unknown'),  # 处理未知类别
                        'bbox': box[i] if i < len(box) else []
                    })

        # 如果没有检测到结果，返回错误
        if not analysis_result:
            return jsonify({'error': 'No objects detected'}), 400

        # ---------- 后续保存和清理逻辑 ----------
        output_dir = os.path.join(app.static_folder, 'results', username)
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f'result_{int(time.time())}.jpg'
        output_path = os.path.join(output_dir, output_filename)
        results[0].save(output_path)

        # 清理旧文件（保留最多5个）
        existing_files = sorted(glob.glob(os.path.join(output_dir, '*.jpg')), key=os.path.getctime)
        for old_file in existing_files[:-5]:
            os.remove(old_file)

        # 保存到数据库
        analysis_data = json.dumps(analysis_result)
        code = f"""
INSERT INTO user_history (user_id, image_path, analysis_results, total_areas)
VALUES (%s, %s, %s, %s)
"""
        web_image_path = f'/static/results/{username}/{output_filename}'

        # 保存 Web 路径到数据库
        params = (user_id, web_image_path, analysis_data, total_areas_json)
        con_my_sql(code, params)

        # 修改返回结果部分（main.py）
        return jsonify({
            'message': 'Analysis completed',
            'results': analysis_result,
            'result_image': web_image_path,  # 使用 Web 路径
            'total_areas': total_areas
        }), 200

        return jsonify({"results": [...]})  # 正确返回 JSON
    except Exception as e:
        import traceback
        traceback.print_exc()  # 打印完整堆栈信息
        app.logger.error(f"分析错误: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500  # 避免泄露敏感信息
if __name__ == '__main__':
    migrate_image_paths()  # 启动时自动执行迁移
    app.run(host='0.0.0.0', port=8000,debug=True)