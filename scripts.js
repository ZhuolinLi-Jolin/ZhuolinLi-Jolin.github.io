// 1. 滚动动画逻辑 (Scroll Animation Logic)
function reveal() {
    var projectContainer = document.querySelector(".project-container");
    var weeklyContainer = document.querySelector(".weekly-link-container");
    var windowHeight = window.innerHeight;
    var elementVisible = 150;

    if (projectContainer) {
        var elementTop = projectContainer.getBoundingClientRect().top;
        if (elementTop < windowHeight - elementVisible) {
            projectContainer.classList.add("reveal");
        }
    }

    if (weeklyContainer) {
        var elementTop = weeklyContainer.getBoundingClientRect().top;
        if (elementTop < windowHeight - elementVisible) {
            weeklyContainer.classList.add("reveal");
        }
    }
}
// 在 DOM 加载后立即执行一次，并监听滚动事件
window.addEventListener("scroll", reveal);
reveal();


// 2. 模态弹窗逻辑 (Modal Logic)
function openAssignments() {
    document.getElementById("assignmentsModal").classList.add("active");
    // 阻止页面滚动 (Prevent page scroll)
    document.body.style.overflow = "hidden"; 
}

function closeAssignments() {
    document.getElementById("assignmentsModal").classList.remove("active");
    // 恢复页面滚动 (Restore page scroll)
    document.body.style.overflow = "auto";
}

// 点击模态背景时关闭 (Close modal when clicking the backdrop)
document.getElementById("assignmentsModal").addEventListener('click', function(e) {
    if (e.target === this) {
        closeAssignments();
    }
});
vegaEmbed('#vis1', 'project/chart1.json').catch(console.error);
vegaEmbed('#vis2', 'project/chart2.json').catch(console.error);
vegaEmbed('#vis5', 'project/chart5.json').catch(console.error);
vegaEmbed('#vis-cc2-1', 'portfolio/cc2-1.json').catch(console.error);
vegaEmbed('#vis-cc2-2', 'portfolio/cc2-2.json').catch(console.error);