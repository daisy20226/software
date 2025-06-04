class EnhancedBackground {
    constructor() {
        this.canvas = document.getElementById('bg-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: 0, y: 0, radius: 150 };
        this.colors = ['#005aff', '#4ECDC4', '#45B7D1', '#11df7d', '#FFEEAD'];
        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        window.addEventListener('mousemove', (e) => this.updateMouse(e));
        window.addEventListener('mouseout', () => this.resetMouse());

        // 创建更多粒子
        for(let i = 0; i < 300; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 4 + 1,
                speedX: Math.random() * 1.2 - 0.6,
                speedY: Math.random() * 1.2 - 0.6,
                color: this.colors[Math.floor(Math.random() * this.colors.length)]
            });
        }

        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    updateMouse(e) {
        this.mouse.x = e.clientX;
        this.mouse.y = e.clientY;
    }

    resetMouse() {
        this.mouse.x = undefined;
        this.mouse.y = undefined;
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // 绘制连接线
        this.ctx.beginPath();
        this.ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        this.ctx.lineWidth = 0.5;

        this.particles.forEach((particle, index) => {
            // 绘制粒子轨迹
            this.ctx.fillStyle = `hsla(${Math.random() * 360}, 50%, 50%, 0.3)`;
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size * 2, 0, Math.PI * 2);
            this.ctx.fill();

            // 粒子运动
            particle.x += particle.speedX;
            particle.y += particle.speedY;

            // 边界反弹
            if(particle.x > this.canvas.width || particle.x < 0)
                particle.speedX *= -1;
            if(particle.y > this.canvas.height || particle.y < 0)
                particle.speedY *= -1;

            // 鼠标交互
            if(this.mouse.x && this.mouse.y) {
                const dx = particle.x - this.mouse.x;
                const dy = particle.y - this.mouse.y;
                const distance = Math.sqrt(dx*dx + dy*dy);

                if(distance < this.mouse.radius) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(particle.x, particle.y);
                    this.ctx.lineTo(this.mouse.x, this.mouse.y);
                    this.ctx.stroke();

                    // 吸引力效果
                    particle.x -= dx * 0.03;
                    particle.y -= dy * 0.03;
                }
            }

            // 粒子间连接
            for(let j = index; j < this.particles.length; j++) {
                const a = this.particles[index];
                const b = this.particles[j];
                const dx = a.x - b.x;
                const dy = a.y - b.y;
                const distance = Math.sqrt(dx*dx + dy*dy);

                if(distance < 100) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(a.x, a.y);
                    this.ctx.lineTo(b.x, b.y);
                    this.ctx.stroke();
                    this.ctx.strokeStyle = `rgba(255,255,255,${1 - distance/100})`;
                }
            }
        });

        requestAnimationFrame(() => this.animate());
    }
}

// 初始化增强版动画
new EnhancedBackground();