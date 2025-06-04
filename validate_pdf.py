import sys
from PyPDF2 import PdfReader

def validate_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        print(f"页数: {len(reader.pages)}")
        print("文件有效！")
    except Exception as e:
        print(f"文件无效: {str(e)}")

if __name__ == "__main__":
    validate_pdf(sys.argv[1])