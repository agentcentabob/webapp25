// service worker
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/static/js/serviceworker.js") 
      .then(res => console.log("Service Worker registered!", res))
      .catch(err => console.log("Service Worker registration failed:", err));
  });
}

// collapsible sidebar
const sidebar = document.getElementById('sidebar');
const toggle = document.getElementById('toggleSidebar');

toggle.addEventListener('click', () => {
  sidebar.classList.toggle('collapsed');
});