document.addEventListener('DOMContentLoaded', () => {
    // 幻灯片元素和配置
    const slides = document.querySelectorAll('.text-slide');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    let currentIndex = 0;
    let autoPlayInterval;

    // 初始化指示器
    function initIndicators() {
        const container = document.getElementById('indicators');
        slides.forEach((_, index) => {
            const indicator = document.createElement('div');
            indicator.className = `indicator ${index === 0 ? 'active' : ''}`;
            indicator.addEventListener('click', () => goToSlide(index));
            container.appendChild(indicator);
        });
    }

    // 幻灯片切换核心方法
    function goToSlide(index) {
        slides[currentIndex].classList.remove('active');
        slides[currentIndex].classList.add('prev');

        currentIndex = (index + slides.length) % slides.length;

        slides.forEach(slide => slide.classList.remove('prev'));
        slides[currentIndex].classList.add('active');

        updateIndicators();
        resetAutoPlay();
    }

    // 导航控制
    function nextSlide() { goToSlide(currentIndex + 1); }
    function prevSlide() { goToSlide(currentIndex - 1); }

    // 更新指示器状态
    function updateIndicators() {
        document.querySelectorAll('.indicator').forEach((indicator, index) => {
            indicator.classList.toggle('active', index === currentIndex);
        });
    }

    // 自动播放控制
    function resetAutoPlay() {
        clearInterval(autoPlayInterval);
        autoPlayInterval = setInterval(nextSlide, 5000);
    }

    // 事件监听
    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') prevSlide();
        if (e.key === 'ArrowRight') nextSlide();
    });

    // 初始化
    initIndicators();
    resetAutoPlay();
});