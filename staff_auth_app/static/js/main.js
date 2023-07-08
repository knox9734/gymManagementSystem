// main.js

document.addEventListener("DOMContentLoaded", function() {
    var popup = document.getElementById('popup');
    if (popup) {
        setTimeout(function() {
            popup.style.display = 'none';
        }, 3000);
    }
});
