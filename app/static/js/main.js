// Refresh functions (keep these)
function refreshScoreboard() {
  fetch('/refresh_scoreboard')
    .then(response => response.text())
    .then(html => {
      document.getElementById('scoreboard-section').innerHTML = html;
    })
    .catch(err => console.log('Error refreshing:', err));
}

function refreshExercise() {
  fetch('/refresh_exercise')
    .then(response => response.text())
    .then(html => {
      document.getElementById('exercise-section').innerHTML = html;
    })
    .catch(err => console.log('Error refreshing:', err));
}

// Wait for DOM to load before setting up modals
document.addEventListener("DOMContentLoaded", function () {
  // --- Share Modal ---
  const shareModal = document.getElementById("shareModal");
  const openShareBtn = document.getElementById("openShareModal");
  const closeShareBtn = document.getElementById("closeShareModal");

  if (openShareBtn && shareModal && closeShareBtn) {
    openShareBtn.onclick = () => shareModal.style.display = "block";
    closeShareBtn.onclick = () => shareModal.style.display = "none";
    window.onclick = (event) => {
      if (event.target === shareModal) shareModal.style.display = "none";
    };
  }

  // --- Exercise Modal ---
  const exerciseModal = document.getElementById("exerciseModal");
  const openExerciseBtn = document.getElementById("openExerciseModalBtn");
  const closeExerciseBtn = document.getElementById("closeExerciseModal");

  if (openExerciseBtn && exerciseModal && closeExerciseBtn) {
    openExerciseBtn.onclick = () => exerciseModal.style.display = "block";
    closeExerciseBtn.onclick = () => exerciseModal.style.display = "none";
    window.onclick = (event) => {
      if (event.target === exerciseModal) exerciseModal.style.display = "none";
    };
  }

  // --- Meal Modal ---
  const mealModal = document.getElementById("mealModal");
  const openMealBtn = document.getElementById("openMealModalBtn");
  const closeMealBtn = document.getElementById("closeMealModal");

  if (openMealBtn && mealModal && closeMealBtn) {
    openMealBtn.onclick = () => mealModal.style.display = "block";
    closeMealBtn.onclick = () => mealModal.style.display = "none";
    window.onclick = (event) => {
      if (event.target === mealModal) mealModal.style.display = "none";
    };
  }
});

// Initialize refresh functions on load
window.addEventListener('load', refreshScoreboard);
window.addEventListener('load', refreshExercise);