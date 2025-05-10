document.addEventListener("DOMContentLoaded", function () {
    console.log("Exercise modal script loaded");

    const scoreboardModel = document.getElementById("scoreboardModal");
    const openScoreboardBtn = document.getElementById("openScoreboardBtn");
    const closeScoreboardBtn = document.getElementById("closeScoreboardBtn");

    if (scoreboardModel && openScoreboardBtn && closeScoreboardBtn) {
        openScoreboardBtn.onclick = () => {
        scoreboardModel.style.display = "block";
      };
      closeScoreboardBtn.onclick = () => {
        scoreboardModel.style.display = "none";
        };
        window.onclick = (event) => {
          if (event.target === scoreboardModel) {
            scoreboardModel.style.display = "none";
          }
        };
      } else {
        console.warn("Modal elements not found.");
      }
    });