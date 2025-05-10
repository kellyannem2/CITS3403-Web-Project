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
  const submitChooseBtn  = document.getElementById('submitChooseBtn');  // ← grab it now

  // ─── Initialize Flatpickr ─────────────────────────────────────────────────
  if (window.flatpickr) {
    flatpickr('.date-picker', {
      enableTime:    true,
      dateFormat:    'Y-m-d H:i',
      defaultDate:   new Date(),
      minuteIncrement: 1
    });
  }

  // ─── Disable the “Add Selected Food” button initially ──────────────────────
  submitChooseBtn.disabled = true;

  // ─── Modal Open/Close ─────────────────────────────────────────────────────
  openBtn.addEventListener('click', () => {
    modal.classList.add('show');
    chooseTabBtn.click();  // reset to the first tab
    // reset pickers
    document.querySelectorAll('.date-picker').forEach(dp => {
      if (dp._flatpickr) dp._flatpickr.setDate(new Date());
    });
    submitChooseBtn.disabled = true;  // reset button
    resultsDiv.innerHTML = '';        // clear any old results
    searchInput.value = '';           // clear search box
  });
  closeBtn.addEventListener('click', () => modal.classList.remove('show'));
  modal.addEventListener('click', e => {
    if (e.target === modal) modal.classList.remove('show');
  });

  // ─── Tab Switching ─────────────────────────────────────────────────────────
  function showChoose() {
    chooseTabBtn.classList.add('active');
    inputTabBtn.classList.remove('active');
    choosePanel.classList.add('active');
    inputPanel.classList.remove('active');
  }
  function showInput() {
    inputTabBtn.classList.add('active');
    chooseTabBtn.classList.remove('active');
    inputPanel.classList.add('active');
    choosePanel.classList.remove('active');
  }
  chooseTabBtn.addEventListener('click', showChoose);
  inputTabBtn.addEventListener('click', showInput);
  showChoose(); // default

  // ─── Search & Select Logic ─────────────────────────────────────────────────
  searchBtn.addEventListener('click', async () => {
    const q = searchInput.value.trim();
    if (!q) return;
    resultsDiv.innerHTML = '<p>Searching…</p>';
    submitChooseBtn.disabled = true;  // in case it was enabled before

    try {
      const res   = await fetch(`/api/foods?q=${encodeURIComponent(q)}`);
      const foods = await res.json();
      const top5  = foods.slice(0,5);

      if (!top5.length) {
        resultsDiv.innerHTML = '<p>No matches found.</p>';
        return;
      }

      resultsDiv.innerHTML = top5.map(f => `
        <div class="food-item" data-id="${f.id||f.fdcId}" data-cal="${f.calories}">
          ${f.name} — ${f.calories} cal
        </div>
      `).join('');

      // Attach click‐to‐select handlers
      resultsDiv.querySelectorAll('.food-item').forEach(el => {
        el.addEventListener('click', () => {
          // clear previous selection highlight
          resultsDiv.querySelectorAll('.food-item.selected').forEach(x => x.classList.remove('selected'));
          // highlight this one
          el.classList.add('selected');

          // fill hidden fields
          document.querySelector('input[name="selected_food_id"]').value  = el.dataset.id;
          document.querySelector('input[name="selected_food_cal"]').value = el.dataset.cal;

          // reflect in input
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
