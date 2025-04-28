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