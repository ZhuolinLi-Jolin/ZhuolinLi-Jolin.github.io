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
// vegaEmbed('#vis1', 'project/chart_1.json').catch(console.error);

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


vegaEmbed('#vis3', 'project/chart_3.json', {actions: false}).catch(console.error);
vegaEmbed('#vis2', 'project/chart_2.json', {actions: false}).catch(console.error);

vegaEmbed('#vis-cc1-1', 'portfolio/cc1-1.json').catch(console.error);
vegaEmbed('#vis-cc1-2', 'portfolio/cc1-2.json').catch(console.error);
vegaEmbed('#vis-cc2-1', 'portfolio/cc2-1.json').catch(console.error);
vegaEmbed('#vis-cc2-2', 'portfolio/cc2-2.json').catch(console.error);
vegaEmbed('#vis-cc3-1', 'portfolio/cc3-1.json').catch(console.error);
vegaEmbed('#vis-cc3-2', 'portfolio/cc3-2.json').catch(console.error);
vegaEmbed('#vis-cc4-1', 'portfolio/cc4-1.json').catch(console.error);   
vegaEmbed('#vis-cc4-2', 'portfolio/cc4-2.json').catch(console.error);
vegaEmbed('#vis-cc5-1', 'portfolio/cc5-1.json').catch(console.error);
vegaEmbed('#vis-cc5-2', 'portfolio/cc5-2.json').catch(console.error);
vegaEmbed('#vis-cc7-1', 'portfolio/cc7-1.json').catch(console.error);
vegaEmbed('#vis-cc7-2', 'portfolio/cc7-2.json').catch(console.error);
vegaEmbed('#vis-cc9-1', 'portfolio/cc9-1.json').catch(console.error);
vegaEmbed('#vis-cc9-2', 'portfolio/cc9-2.json').catch(console.error);

// CC6: Loop to embed six charts
for (let i = 1; i <= 6; i++) {
    vegaEmbed(`#vis-cc6-${i}`, `portfolio/cc6-${i}.json`, {actions: false}).catch(console.error);
}