// Exercise Log Modal (on exercise log page not on dashboard)
document.addEventListener("DOMContentLoaded", function () {
    console.log("Script is loaded");
  
  const logModal = document.getElementById("logModal");
  const openLogModalBtn = document.getElementById("openLogModalBtn");
  const closeLogModalBtn = document.getElementById("closeLogModal");
  
  if (openLogModalBtn && logModal && closeLogModalBtn) {
    openLogModalBtn.onclick = () => {
      logModal.style.display = "block";
    };
  
    closeLogModalBtn.onclick = () => {
      logModal.style.display = "none";
    };
  
    window.onclick = function (event) {
      if (event.target == logModal) {
        logModal.style.display = "none";
      }
    };
  }
  });