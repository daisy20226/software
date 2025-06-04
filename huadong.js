// 选择所有.box元素
const boxes = document.querySelectorAll('.box');

// 监听窗口滚动事件
window.addEventListener('scroll', function () {
    // 获取窗口的高度
    const windowHeight = window.innerHeight;

    // 遍历每个.box元素
    boxes.forEach(box => {
        // 获取.box元素距离视口顶部的距离
        const boxTop = box.getBoundingClientRect().top;

        // 检查.box元素是否进入可视区域
        if (boxTop < windowHeight) {
            // 如果进入可视区域，添加.show类以触发动画
            box.classList.add('show');
        }
    });
});