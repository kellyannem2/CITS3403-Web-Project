document.addEventListener("DOMContentLoaded", function () {
  console.log("Script is loaded");

  const logModal = document.getElementById("countModal");
  const openLogModalBtn = document.getElementById("openCountModalBtn");
  const closeLogModalBtn = document.getElementById("closeCountModal");

  flatpickr(".date-picker", {
    enableTime: true,
    dateFormat: "Y-m-d H:i",
  });

  if (openLogModalBtn && logModal && closeLogModalBtn) {
    openLogModalBtn.onclick = () => {
      logModal.style.display = "block";
    };

    closeLogModalBtn.onclick = () => {
      logModal.style.display = "none";
    };

    window.onclick = function (event) {
      if (event.target === logModal) {
        logModal.style.display = "none";
      }
    };
  }

  document.addEventListener("click", function (e) {
    if (e.target.classList.contains("food-result")) {
      const selected = e.target.dataset;

      const idField = document.querySelector("input[name='selected_food_id']");
      const fdcField = document.querySelector("input[name='fdc_id']");
      const calField = document.querySelector("input[name='selected_food_cal']");

      if (idField)  idField.value = selected.id || '';
      if (fdcField) fdcField.value = selected.fdcId || '';
      if (calField) calField.value = selected.calories || '';
    }
  });
});
