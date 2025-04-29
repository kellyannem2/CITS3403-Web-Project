// Calorie Counter Modal (on calorie page not on dashboard)
document.addEventListener("DOMContentLoaded", function () {
    console.log("Script is loaded");
  
  const logModal = document.getElementById("countModal");
  const openLogModalBtn = document.getElementById("openCountModalBtn");
  const closeLogModalBtn = document.getElementById("closeCountModal");
  
  if (openCountModalBtn && countModal && closeCountModalBtn) {
    openCountModalBtn.onclick = () => {
      countModal.style.display = "block";
    };
  
    closeCountModalBtn.onclick = () => {
      countModal.style.display = "none";
    };
  
    window.onclick = function (event) {
      if (event.target == countModal) {
        countModal.style.display = "none";
      }
    };
  }
  });