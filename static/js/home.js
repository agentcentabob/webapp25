// feature  tile interactions
document.addEventListener('DOMContentLoaded', function() {
  const tiles = document.querySelectorAll('.feature-tile');

  tiles.forEach(tile => {
    tile.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-6px) scale(1.02)';
    });

    tile.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0) scale(1)';
    });
  });

  // smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
});