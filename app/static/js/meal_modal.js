// static/js/meal_modal.js
document.addEventListener('DOMContentLoaded', () => {
  // ─── Elements ─────────────────────────────────────────────────────────────
  const openBtn          = document.getElementById('openMealModalBtn');
  const modal            = document.getElementById('mealModal');
  const closeBtn         = document.getElementById('closeMealModalBtn');
  const chooseTabBtn     = document.getElementById('chooseFoodTabBtn');
  const inputTabBtn      = document.getElementById('inputOwnTabBtn');
  const choosePanel      = document.getElementById('chooseFoodTab');
  const inputPanel       = document.getElementById('inputOwnTab');
  const searchInput      = document.getElementById('searchFoodInput');
  const searchBtn        = document.getElementById('searchFoodBtn');
  const resultsDiv       = document.getElementById('foodResults');
  const submitChooseBtn  = document.getElementById('submitChooseBtn');

  // Custom tab inputs
  const customNameInput     = document.querySelector('input[name="custom_name"]');
  const customCaloriesInput = document.querySelector('input[name="custom_calories"]');

  // ─── Initialize Flatpickr ─────────────────────────────────────────────────
  if (window.flatpickr) {
    flatpickr('.date-picker', {
      enableTime:      true,
      dateFormat:      'Y-m-d\\TH:i',  // emit 2025-05-10T19:46
      defaultDate:     new Date(),
      minuteIncrement: 1
    });
  }

  // ─── Disable the “Add Selected Food” button initially ──────────────────────
  submitChooseBtn.disabled = true;

  // ─── Modal Open/Close ─────────────────────────────────────────────────────
  openBtn.addEventListener('click', () => {
    modal.classList.add('show');
    activateChoose();  // reset to first tab

    // Reset date-picker
    document.querySelectorAll('.date-picker').forEach(dp => {
      if (dp._flatpickr) dp._flatpickr.setDate(new Date());
    });

    // Reset state
    submitChooseBtn.disabled = true;
    resultsDiv.innerHTML      = '';
    searchInput.value         = '';
  });

  closeBtn.addEventListener('click', () => modal.classList.remove('show'));
  modal.addEventListener('click', e => {
    if (e.target === modal) modal.classList.remove('show');
  });

  // ─── Tab Switching ─────────────────────────────────────────────────────────
  function activateChoose() {
    chooseTabBtn.classList.add('active');
    inputTabBtn.classList.remove('active');
    choosePanel.classList.add('active');
    inputPanel.classList.remove('active');

    // Disable custom fields in search mode
    customNameInput.disabled     = true;
    customCaloriesInput.disabled = true;
  }

  function activateInput() {
    inputTabBtn.classList.add('active');
    chooseTabBtn.classList.remove('active');
    inputPanel.classList.add('active');
    choosePanel.classList.remove('active');

    // Enable custom fields in custom mode
    customNameInput.disabled     = false;
    customCaloriesInput.disabled = false;
  }

  chooseTabBtn.addEventListener('click', activateChoose);
  inputTabBtn.addEventListener('click', activateInput);

  // initialize on load
  activateChoose();

  // ─── Search & Select Logic ─────────────────────────────────────────────────
  searchBtn.addEventListener('click', async () => {
    const q = searchInput.value.trim();
    if (!q) return;
    resultsDiv.innerHTML       = '<p>Searching…</p>';
    submitChooseBtn.disabled   = true;

    try {
      const res   = await fetch(`/api/foods?q=${encodeURIComponent(q)}`);
      const foods = await res.json();
      const top5  = foods.slice(0, 5);

      if (!top5.length) {
        resultsDiv.innerHTML = '<p>No matches found.</p>';
        return;
      }

      resultsDiv.innerHTML = top5.map(f => `
        <div class="food-item" data-id="${f.id||f.fdcId}" data-cal="${f.calories}">
          ${f.name} — ${f.calories} cal
        </div>
      `).join('');

      // Attach click-to-select
      resultsDiv.querySelectorAll('.food-item').forEach(el => {
        el.addEventListener('click', () => {
          // clear previous selected
          resultsDiv.querySelectorAll('.food-item.selected').forEach(x => x.classList.remove('selected'));
          el.classList.add('selected');

          // populate hidden fields
          const selectedIdField = document.querySelector('input[name="selected_food_id"]');
          const fdcIdField      = document.querySelector('input[name="fdc_id"]');
          const calField        = document.querySelector('input[name="selected_food_cal"]');

          // Detect source by checking if ID is numeric and large (USDA fdcIds are 6-7 digits)
          const isUsdaFood = el.dataset.id && el.dataset.id.length >= 6;

        if (isUsdaFood) {
          selectedIdField.value = "";
          fdcIdField.value      = el.dataset.id;
        } else {
          selectedIdField.value = el.dataset.id;
          fdcIdField.value      = "";
        }

calField.value = el.dataset.cal || "";


          // reflect in search box
          searchInput.value = el.textContent.split(' — ')[0];

          // enable submit
          submitChooseBtn.disabled = false;
        });
      });
    } catch (err) {
      console.error('Food search failed:', err);
      resultsDiv.innerHTML = '<p style="color:red;">Error searching foods.</p>';
    }
  });
});
