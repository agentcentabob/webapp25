if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/static/js/serviceworker.js") 
      .then(res => console.log("Service Worker registered!", res))
      .catch(err => console.log("Service Worker registration failed:", err));
  });
}

// sidebar opening and closing system //
function openNav() {
  document.getElementById("mySidenav").style.width = "250px";
}

function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
}

// check for menu page
const accountButton = document.querySelector('.accountzone');

if (accountButton) {
  function updateAccountButton() {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    
    if (isLoggedIn) {
      accountButton.textContent = 'Logout';
      accountButton.classList.remove('login');
      accountButton.classList.add('logout');
    } else {
      accountButton.textContent = 'Login';
      accountButton.classList.remove('logout');
      accountButton.classList.add('login');
    }
  }
  
  updateAccountButton();
  
  accountButton.addEventListener('click', () => {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    
    if (isLoggedIn) {
      localStorage.setItem('isLoggedIn', 'false');
      window.location.href = 'login.html';
    } else {
      window.location.href = 'login.html';
    }
  });
}