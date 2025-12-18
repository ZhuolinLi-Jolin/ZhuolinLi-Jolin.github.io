// 1. Scroll Animation Logic
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
// Execute once after DOM loads and listen to scroll events
window.addEventListener("scroll", reveal);
reveal();


// 2. Modal Logic
function openAssignments() {
    document.getElementById("assignmentsModal").classList.add("active");
    // Prevent page scroll
    document.body.style.overflow = "hidden"; 
}

function closeAssignments() {
    document.getElementById("assignmentsModal").classList.remove("active");
    // Restore page scroll
    document.body.style.overflow = "auto";
}

// Close modal when clicking the backdrop
document.getElementById("assignmentsModal").addEventListener('click', function(e) {
    if (e.target === this) {
        closeAssignments();
    }
});
// vegaEmbed('#vis1', 'project/chart_1.json').catch(console.error);

const plotFileName = 'project/chart_1.json';
// fetch('project/chart_1.json') // Ensure path is correct
//   .then(response => response.json())
//   .then(plotlyData => {
//       Plotly.newPlot('vis1', plotlyData.data, plotlyData.layout);
//       console.log("Plotly chart loaded successfully.");
//   })
//   .catch(error => console.error('Error loading Plotly chart:', error));
fetch(plotFileName)
  .then(response => response.json())
  .then(fig => {
      // The JSON structure you provided is standard {data: ..., layout: ...}
      // So we can directly take fig.data and fig.layout
      Plotly.newPlot('vis1', fig.data, fig.layout);
      
      console.log("✅ Chart rendered successfully!");
  })
  .catch(error => {
      console.error("❌ Rendering failed:", error);
  });

vegaEmbed('#vis2', 'project/chart_2.json').catch(console.error);
vegaEmbed('#vis5', 'project/chart5.json').catch(console.error);
vegaEmbed('#vis-cc2-1', 'portfolio/cc2-1.json').catch(console.error);
vegaEmbed('#vis-cc2-2', 'portfolio/cc2-2.json').catch(console.error);