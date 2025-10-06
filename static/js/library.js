// search and filters
const searchInput = document.getElementById('searchInput');
const sortSelect = document.getElementById('sortSelect');
const notesGrid = document.getElementById('notesGrid');
const noteCards = notesGrid ? Array.from(notesGrid.querySelectorAll('.note-card')) : [];

// search
if (searchInput) {
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();
        
        noteCards.forEach(card => {
            const title = card.dataset.title || '';
            const location = card.dataset.location || '';
            
            if (title.includes(query) || location.includes(query)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// sorting
if (sortSelect) {
    sortSelect.addEventListener('change', function(e) {
        const sortBy = e.target.value;
        
        const sorted = [...noteCards].sort((a, b) => {
            switch(sortBy) {
                case 'recent':
                    return new Date(b.dataset.date) - new Date(a.dataset.date);
                case 'oldest':
                    return new Date(a.dataset.date) - new Date(b.dataset.date);
                case 'title':
                    return a.dataset.title.localeCompare(b.dataset.title);
                case 'location':
                    const locA = a.dataset.location || 'zzz';
                    const locB = b.dataset.location || 'zzz';
                    return locA.localeCompare(locB);
                default:
                    return 0;
            }
        });
        
        // reappend in sorted order
        sorted.forEach(card => notesGrid.appendChild(card));
    });
}