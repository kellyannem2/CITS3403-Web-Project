// Exercise Log Modal 
// Adding exercises in dynamically from the Exercises Page

document.addEventListener("DOMContentLoaded", function () {
    console.log("Exercise modal script loaded");

    const exerciseModal = document.getElementById("exerciseModal");
    const openExerciseBtn = document.getElementById("openExerciseModalBtn");
    const closeExerciseBtn = document.getElementById("closeExerciseModal");

    if (openExerciseBtn && exerciseModal && closeExerciseBtn) {
      openExerciseBtn.onclick = () => {
        exerciseModal.style.display = "block";
      };
        closeExerciseBtn.onclick = () => {
          exerciseModal.style.display = "none";
        };
        window.onclick = (event) => {
          if (event.target === exerciseModal) {
            exerciseModal.style.display = "none";
          }
        };
      } else {
        console.warn("Modal elements not found.");
      }
    });