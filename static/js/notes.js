// notes.js - JavaScript for markdown note editor
// Wrap everything in an IIFE to avoid conflicts with other scripts
(function() {
    'use strict';
    
    let currentNoteId = null;
    let autoSaveTimeout;
    let easyMDE;

    // Initialize EasyMDE when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Only initialize if we're on the notes page
        if (!document.getElementById('noteContent')) {
            return;
        }
        
        initEditor();
    });

    // Initialize EasyMDE editor
    function initEditor() {
        // Check if EasyMDE is loaded
        if (typeof EasyMDE === 'undefined') {
            console.error('EasyMDE library not loaded. Check CDN link or Content Security Policy.');
            alert('Editor library failed to load. Please check your internet connection or contact support.');
            return;
        }
        
        easyMDE = new EasyMDE({
            element: document.getElementById('noteContent'),
            spellChecker: false,
            autofocus: true,
            placeholder: "Start typing your note... Markdown is supported!\n\n# Heading 1\n## Heading 2\n**Bold** and *italic*\n- List item\n\n[Link](url)",
            status: false,
            toolbar: [
                "bold", "italic", "heading", "|",
                "quote", "unordered-list", "ordered-list", "|",
                "link", "image", "|",
                "preview", "side-by-side", "fullscreen", "|",
                "guide"
            ],
            minHeight: "500px",
            renderingConfig: {
                singleLineBreaks: false,
                codeSyntaxHighlighting: true,
            }
        });

        // Auto-save on content change
        easyMDE.codemirror.on("change", function() {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                if (currentNoteId) {
                    saveNote();
                }
            }, 2000);
        });

        // Load initial content from page data
        const noteIdElement = document.getElementById('noteIdData');
        const noteTitleElement = document.getElementById('noteTitleData');
        const noteContentElement = document.getElementById('noteContentData');
        
        if (noteIdElement && noteIdElement.value) {
            currentNoteId = parseInt(noteIdElement.value);
        }
        
        if (noteTitleElement && noteTitleElement.value) {
            document.getElementById('noteTitle').value = noteTitleElement.value;
        }
        
        if (noteContentElement && noteContentElement.value) {
            easyMDE.value(noteContentElement.value);
        }
        
        // Auto-save on title change
        const titleInput = document.getElementById('noteTitle');
        if (titleInput) {
            titleInput.addEventListener('input', () => {
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(() => {
                    if (currentNoteId) {
                        saveNote();
                    }
                }, 2000);
            });
        }
    }

    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveNote);
    }
    
    // Delete button click handler
    const deleteBtn = document.getElementById('deleteBtn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', deleteNote);
    }

    // Get current note data
    function getCurrentNoteData() {
        return {
            title: document.getElementById('noteTitle').value,
            content: easyMDE.value()
        };
    }

    // Save the current note
    function saveNote() {
        if (!currentNoteId) {
            // Create new note
            createNote();
            return;
        }

        const noteData = getCurrentNoteData();
        
        fetch('/api/notes/' + currentNoteId, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(noteData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateLastSaved('Saved at ' + new Date().toLocaleTimeString());
                console.log('Note saved successfully');
            } else {
                console.error('Error saving note:', data.error);
                alert('Error saving note: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error saving note. Please check your connection.');
        });
    }

    // Create a new note
    function createNote() {
        const noteData = getCurrentNoteData();
        
        fetch('/api/notes', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(noteData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentNoteId = data.note_id;
                updateLastSaved('Saved at ' + new Date().toLocaleTimeString());
                // Update URL without reload
                window.history.pushState({}, '', '/notes/' + data.note_id);
                console.log('Note created successfully');
            } else {
                console.error('Error creating note:', data.error);
                alert('Error creating note: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error creating note. Please check your connection.');
        });
    }

    // Delete the current note
    function deleteNote() {
        if (!currentNoteId) {
            alert('No note to delete');
            return;
        }

        if (!confirm('Are you sure you want to delete this note?')) {
            return;
        }

        fetch('/api/notes/' + currentNoteId, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect to notes list
                window.location.href = '/notes';
            } else {
                console.error('Error deleting note:', data.error);
                alert('Error deleting note: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting note. Please check your connection.');
        });
    }

    // Update last saved timestamp
    function updateLastSaved(text) {
        const lastSavedElement = document.getElementById('lastSaved');
        if (lastSavedElement) {
            lastSavedElement.textContent = text;
        }
    }

    // Expose functions globally so onclick handlers work
    window.saveNote = saveNote;
    window.deleteNote = deleteNote;
})();