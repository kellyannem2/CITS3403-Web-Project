document.addEventListener('DOMContentLoaded', () => {
  // Modal logic
  const scoreboardModal = document.getElementById('scoreboardModal');
  const openScoreboardBtn = document.getElementById('openScoreboardBtn');
  const closeScoreboardBtn = document.getElementById('closeScoreboardBtn');
  if (scoreboardModal && openScoreboardBtn && closeScoreboardBtn) {
    openScoreboardBtn.onclick = () => scoreboardModal.style.display = 'block';
    closeScoreboardBtn.onclick = () => scoreboardModal.style.display = 'none';
    window.onclick = (e) => { if (e.target === scoreboardModal) scoreboardModal.style.display = 'none'; };
  } else {
    console.warn('Modal elements not found.');
  }

  // Sorting logic
  const table = document.getElementById('leaderboard-table');
  if (!table) return;

  const headers = table.querySelectorAll('th[data-key]');
  const tbody = table.querySelector('tbody');

  // Save original header labels
  headers.forEach(h => { h.dataset.original = h.textContent.trim(); });

  // Initial sort by net descending without arrow indicator
  sortTable('net', false);

  headers.forEach(header => {
    header.style.cursor = 'pointer';
    header.addEventListener('click', () => {
      const key = header.dataset.key;
      const asc = header.dataset.order !== 'asc';
      // Reset all headers to original label and clear order
      headers.forEach(h => {
        h.dataset.order = '';
        h.textContent = h.dataset.original;
      });
      // Set this header arrow
      header.dataset.order = asc ? 'asc' : 'desc';
      header.textContent = header.dataset.original + (asc ? ' ▲' : ' ▼');
      sortTable(key, asc);
    });
  });

  function sortTable(key, asc = true) {
    const rows = Array.from(tbody.querySelectorAll('tr'));
    rows.sort((a, b) => {
      const aVal = parseValue(a, key);
      const bVal = parseValue(b, key);
      if (!isNaN(aVal) && !isNaN(bVal)) {
        return asc ? aVal - bVal : bVal - aVal;
      }
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      if (aStr < bStr) return asc ? -1 : 1;
      if (aStr > bStr) return asc ? 1 : -1;
      return 0;
    });
    // Re-append rows in new order (rank cells remain unchanged)
    rows.forEach(row => tbody.appendChild(row));
  }

  function parseValue(row, key) {
    const cell = row.querySelector(`td.${key}`);
    if (!cell) return '';
    const text = cell.textContent.trim();
    const num = parseFloat(text);
    return isNaN(num) ? text : num;
  }
});