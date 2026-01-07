// 1. Scroll Animation Logic
function reveal() {
    var projectContainer = document.querySelector(".project-container");
    var windowHeight = window.innerHeight;
    var elementVisible = 150;

    if (projectContainer) {
        var elementTop = projectContainer.getBoundingClientRect().top;
        if (elementTop < windowHeight - elementVisible) {
            projectContainer.classList.add("reveal");
        }
    }
}
// Execute once after DOM loads and listen to scroll events
window.addEventListener("scroll", reveal);
reveal();


// 2. Modal Logic
function openAssignments() {
    const modal = document.getElementById("assignmentsModal");
    if (modal) {
        modal.classList.add("active");
        // Prevent page scroll
        document.body.style.overflow = "hidden"; 
    }
}

function closeAssignments() {
    const modal = document.getElementById("assignmentsModal");
    if (modal) {
        modal.classList.remove("active");
        // Restore page scroll
        document.body.style.overflow = "auto";
    }
}

// Close modal when clicking the backdrop
const modal = document.getElementById("assignmentsModal");
if (modal) {
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            closeAssignments();
        }
    });
}

const plotFileName = 'project/chart_1.json';

fetch(plotFileName)
  .then(response => response.json())
  .then(fig => {
      // 强制使用原始尺寸渲染
      fig.layout.width = 1100;
      fig.layout.height = 750;

      // 渲染图表
      Plotly.newPlot('vis1', fig.data, fig.layout);

      // 根据包裹层宽度动态计算缩放比例
      const wrapper = document.getElementById('vis1-wrapper');
      const plot = document.getElementById('vis1');
      
      function applyScale() {
          const containerWidth = wrapper.clientWidth;
          const scale = Math.min(containerWidth / 1100, 1); // 不放大,只缩小
          plot.style.transform = `scale(${scale})`;
          // 调整包裹层高度以适应缩放后的图表
          wrapper.style.height = `${750 * scale}px`;
      }
      
      applyScale();
      window.addEventListener('resize', applyScale);

      console.log("✅ Chart rendered and scaled successfully!");
  })
  .catch(error => {
      console.error("❌ Rendering failed:", error);
  });

// Pre-Figure charts on project page
vegaEmbed('#vis-chart01', 'project/chart_01.json', {actions: false, renderer: 'svg'}).then(result => {
    result.view.width(document.getElementById('vis-chart01').offsetWidth).run();
}).catch(console.error);
vegaEmbed('#vis-chart02', 'project/chart_02.json', {actions: false, renderer: 'svg'}).then(result => {
    result.view.width(document.getElementById('vis-chart02').offsetWidth).run();
}).catch(console.error);


vegaEmbed('#vis3', 'project/chart_3.json', {actions: false, renderer: 'svg'}).then(result => {
    result.view.width(document.getElementById('vis3').offsetWidth).run();
}).catch(console.error);
vegaEmbed('#vis2', 'project/chart_2.json', {actions: false, renderer: 'svg'}).then(result => {
    result.view.width(document.getElementById('vis2').offsetWidth).run();
}).catch(console.error);

// Portfolio charts with responsive width
const portfolioCharts = [
    'vis-cc1-1', 'vis-cc1-2', 'vis-cc2-1', 'vis-cc2-2',
    'vis-cc3-1', 'vis-cc3-2', 'vis-cc4-1', 'vis-cc4-2',
    'vis-cc5-1', 'vis-cc5-2', 'vis-cc7-1', 'vis-cc7-2',
    'vis-cc9-1', 'vis-cc9-2', 'vis-cc10-1', 'vis-cc10-2'
];

portfolioCharts.forEach(chartId => {
    const chartPath = `portfolio/${chartId.replace('vis-', '')}.json`;

    // cc1 / cc3 特殊处理：缩小宽度并提升高度，保持自适应
    if (['vis-cc1-1', 'vis-cc1-2', 'vis-cc3-1', 'vis-cc3-2', 'vis-cc9-1'].includes(chartId)) {
        vegaEmbed(`#${chartId}`, chartPath, {actions: false, renderer: 'svg'})
            .then(result => {
                const container = document.getElementById(chartId);
                if (!container) return;

                const applySize = () => {
                    const targetWidth = Math.round(container.offsetWidth * 0.65);
                    const targetHeight = Math.round(targetWidth * 0.6);
                    result.view.width(targetWidth).height(targetHeight).run();
                };

                applySize();
                window.addEventListener('resize', applySize);
            })
            .catch(console.error);
        return;
    }

    // 默认处理：宽度适配容器宽度
    vegaEmbed(`#${chartId}`, chartPath, {actions: false, renderer: 'svg'})
        .then(result => {
            const container = document.getElementById(chartId);
            if (container) {
                result.view.width(container.offsetWidth).run();
            }
        })
        .catch(console.error);
});

// CC6: Loop to embed six charts with responsive width
for (let i = 1; i <= 6; i++) {
    vegaEmbed(`#vis-cc6-${i}`, `portfolio/cc6-${i}.json`, {actions: false, renderer: 'svg'}).then(result => {
        const container = document.getElementById(`vis-cc6-${i}`);
        if (container) {
            result.view.width(container.offsetWidth).run();
        }
    }).catch(console.error);
}