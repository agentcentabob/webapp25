const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');

toggleBtn.addEventListener('click', () => {
  sidebar.classList.toggle('collapsed');
  
  // adjust main margin
  mainContent.style.marginLeft = sidebar.classList.contains('collapsed') ? '60px' : '160px';
  
  // change link text when collapsed
  const links = sidebar.querySelectorAll('.link-text');
  links.forEach(link => {
    if(sidebar.classList.contains('collapsed')) {
      link.textContent = ''; // or a short icon/letter
    } else {
      // restore full text
      const fullText = link.getAttribute('data-full') || link.textContent;
      link.textContent = fullText;
    }
  });
});

// store full text in data attribute for restoration
document.querySelectorAll('.link-text').forEach(link => {
  link.setAttribute('data-full', link.textContent);
});