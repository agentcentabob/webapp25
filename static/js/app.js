if ("serviceworker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceworker
      .register("js/serviceworker.js")
      .then((res) => console.log("service worker registered"))
      .catch((err) => console.log("service worker not registered", err));
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

// Check if we're on the login page (has a login form)
const loginForm = document.querySelector('/login'); // adjust selector if needed

if (loginForm) {
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    // Your login logic here
    // If login successful:
    localStorage.setItem('isLoggedIn', 'true');
    
    window.location.href = 'menu.html';
  });
}