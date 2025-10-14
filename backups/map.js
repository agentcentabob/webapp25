// /static/js/
document.addEventListener('DOMContentLoaded', function() {
  // Initialize map centered on your region
  const map = L.map('map').setView([-33.8, 150.4], 10);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19
}).addTo(map);

// Fetch your notes with locations from your backend
fetch('/api/notes-locations')
  .then(response => response.json())
  .then(data => {
    data.forEach(note => {
      // Geocode the text location to get coordinates
      fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(note.location)}&format=json`)
        .then(res => res.json())
        .then(results => {
          if (results.length > 0) {
            const lat = results[0].lat;
            const lng = results[0].lon;
            
            // Add marker to map
            L.marker([lat, lng])
              .bindPopup(`<b>${note.title}</b><br>${note.location}`)
              .addTo(map);
          }
        });
    });
  })
      .catch(err => console.error('Error loading notes:', err));
});