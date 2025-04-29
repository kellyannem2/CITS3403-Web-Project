function refreshScoreboard() {
    fetch('/refresh_scoreboard')
        .then(response => response.text())
        .then(html => {
            document.getElementById('scoreboard-section').innerHTML = html;
        })
        .catch(err => console.log('Error refreshing:', err));
}
window.addEventListener('load', refreshScoreboard);

function refreshExercise() {
    fetch('/refresh_exercise')
        .then(response => response.text())
        .then(html => {
            document.getElementById('exercise-section').innerHTML = html;
        })
        .catch(err => console.log('Error refreshing:', err));
}
window.addEventListener('load', refreshExercise);

// Exercise Modal
const exerciseModal = document.getElementById("modal");
const openExerciseBtn = document.getElementById("openModalBtn");
const closeExerciseBtn = document.querySelector(".close-btn");

openExerciseBtn.onclick = () => {
  exerciseModal.style.display = "block";
};

closeExerciseBtn.onclick = () => {
  exerciseModal.style.display = "none";
};

// Meal Modal
const mealModal = document.getElementById("mealModal");
const openMealBtn = document.getElementById("openMealModalBtn");
const closeMealBtn = document.getElementById("closeMealModal");

openMealBtn.onclick = () => {
  mealModal.style.display = "block";
};

closeMealBtn.onclick = () => {
  mealModal.style.display = "none";
};

// Close modals if outside is clicked
window.onclick = function (event) {
  if (event.target == exerciseModal) {
    exerciseModal.style.display = "none";
  }
  if (event.target == mealModal) {
    mealModal.style.display = "none";
  }
};
