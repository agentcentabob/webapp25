// DOM Elements
const searchInput = document.getElementById('searchInput');
const sortSelect = document.getElementById('sortSelect');
const notesGrid = document.getElementById('notesGrid');
const notesList = document.getElementById('notesList');

// Get all note cards and list items
const noteCards = notesGrid ? Array.from(notesGrid.querySelectorAll('.note-card')) : [];
const noteListItems = notesList ? Array.from(notesList.querySelectorAll('.note-list-item')) : [];

// View toggle elements
const viewBtns = document.querySelectorAll('.view-btn');
let currentView = 'grid';

// Modal elements
const renameModal = document.getElementById('renameModal');
const deleteModal = document.getElementById('deleteModal');
const renameInput = document.getElementById('renameInput');
const deleteNoteName = document.getElementById('deleteNoteName');
const renameCancelBtn = document.getElementById('renameCancelBtn');
const renameConfirmBtn = document.getElementById('renameConfirmBtn');
const deleteCancelBtn = document.getElementById('deleteCancelBtn');
const deleteConfirmBtn = document.getElementById('deleteConfirmBtn');

let currentNoteId = null;

// ============================================
// SEARCH FUNCTIONALITY
// ============================================
if (searchInput) {
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();
        
        // Search in current view
        const items = currentView === 'grid' ? noteCards : noteListItems;
        
        items.forEach(item => {
            const title = item.dataset.title || '';
            const location = item.dataset.location || '';
            
            if (title.includes(query) || location.includes(query)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

// ============================================
// SORTING FUNCTIONALITY
// ============================================
if (sortSelect) {
    sortSelect.addEventListener('change', function(e) {
        const sortBy = e.target.value;
        
        // Sort both views
        sortNotes(noteCards, notesGrid, sortBy);
        sortNotes(noteListItems, notesList, sortBy);
    });
}

function sortNotes(items, container, sortBy) {
    const sorted = [...items].sort((a, b) => {
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
    
    // Reappend in sorted order
    sorted.forEach(item => container.appendChild(item));
}

// ============================================
// VIEW TOGGLE FUNCTIONALITY
// ============================================
viewBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        const view = this.dataset.view;
        
        // Update active button
        viewBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        // Toggle views
        if (view === 'grid') {
            notesGrid.classList.add('active');
            notesList.classList.remove('active');
            currentView = 'grid';
        } else {
            notesGrid.classList.remove('active');
            notesList.classList.add('active');
            currentView = 'list';
        }
        
        // Reapply search filter to new view
        if (searchInput.value) {
            searchInput.dispatchEvent(new Event('input'));
        }
    });
});

// ============================================
// RENAME FUNCTIONALITY
// ============================================
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('rename') || e.target.closest('.rename')) {
        e.preventDefault();
        e.stopPropagation();
        
        const btn = e.target.classList.contains('rename') ? e.target : e.target.closest('.rename');
        currentNoteId = btn.dataset.noteId;
        const currentTitle = btn.dataset.currentTitle;
        
        renameInput.value = currentTitle;
        renameModal.classList.add('active');
        renameInput.focus();
        renameInput.select();
    }
});

renameCancelBtn.addEventListener('click', closeRenameModal);

renameConfirmBtn.addEventListener('click', function() {
    const newTitle = renameInput.value.trim();
    
    if (!newTitle) {
        renameInput.focus();
        return;
    }
    
    // Create a form and submit it (uses Flask flash system)
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/notes/${currentNoteId}/rename`;
    
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'title';
    input.value = newTitle;
    
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
});

// Allow Enter key to confirm rename
renameInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        renameConfirmBtn.click();
    }
});

function closeRenameModal() {
    renameModal.classList.remove('active');
    currentNoteId = null;
}

// ============================================
// DELETE FUNCTIONALITY
// ============================================
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('delete') || e.target.closest('.delete')) {
        e.preventDefault();
        e.stopPropagation();
        
        const btn = e.target.classList.contains('delete') ? e.target : e.target.closest('.delete');
        currentNoteId = btn.dataset.noteId;
        const noteTitle = btn.dataset.title;
        
        deleteNoteName.textContent = noteTitle;
        deleteModal.classList.add('active');
    }
});

deleteCancelBtn.addEventListener('click', closeDeleteModal);

deleteConfirmBtn.addEventListener('click', function() {
    // Create a form and submit it (uses Flask flash system)
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/notes/${currentNoteId}/delete`;
    document.body.appendChild(form);
    form.submit();
});

function closeDeleteModal() {
    deleteModal.classList.remove('active');
    currentNoteId = null;
}

// ============================================
// CLOSE MODALS ON OUTSIDE CLICK
// ============================================
renameModal.addEventListener('click', function(e) {
    if (e.target === renameModal) {
        closeRenameModal();
    }
});

deleteModal.addEventListener('click', function(e) {
    if (e.target === deleteModal) {
        closeDeleteModal();
    }
});

// ============================================
// CLOSE MODALS ON ESC KEY
// ============================================
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeRenameModal();
        closeDeleteModal();
    }
});