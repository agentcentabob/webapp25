if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/static/js/serviceworker.js") 
      .then(res => console.log("Service Worker registered!", res))
      .catch(err => console.log("Service Worker registration failed:", err));
  });
}