// notes.js - With autosave functionality
(function() {
    'use strict';
    
    let easyMDE;
    let autoSaveTimeout;
    let hasChanges = false;

    document.addEventListener('DOMContentLoaded', function() {
        if (!document.getElementById('noteContent')) {
            return;
        }
        
        initEditor();
    });

    function initEditor() {
        if (typeof EasyMDE === 'undefined') {
            console.error('EasyMDE library not loaded.');
            alert('Editor library failed to load. Please refresh the page.');
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

        // Auto-save on content change (5 seconds after stopping typing)
        easyMDE.codemirror.on("change", function() {
            hasChanges = true;
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                autoSave();
            }, 5000);
        });

        // Auto-save on title change
        const titleInput = document.getElementById('noteTitle');
        if (titleInput) {
            titleInput.addEventListener('input', () => {
                hasChanges = true;
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(() => {
                    autoSave();
                }, 5000);
            });
        }

        // Handle delete button
        const deleteBtn = document.getElementById('deleteBtn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                if (confirm('Are you sure you want to delete this note?')) {
                    document.getElementById('deleteForm').submit();
                }
            });
        }

        // Before form submission, sync EasyMDE content to textarea
        const form = document.getElementById('noteForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                const textarea = document.getElementById('noteContent');
                textarea.value = easyMDE.value();
            });
        }
    }

    function autoSave() {
        if (!hasChanges) return;
        
        // Sync EasyMDE content to textarea
        const textarea = document.getElementById('noteContent');
        textarea.value = easyMDE.value();
        
        const form = document.getElementById('noteForm');
        const formData = new FormData(form);
        
        // Submit form via fetch without reloading page
        fetch(form.action || window.location.href, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                updateLastSaved('Auto-saved at ' + new Date().toLocaleTimeString());
                hasChanges = false;
                
                // If this was a new note, update URL to point to the note
                return response.text();
            } else {
                updateLastSaved('Error saving');
            }
        })
        .then(html => {
            // Check if we were redirected (new note created)
            // This is a bit hacky but works
            if (html && html.includes('/notes/') && !window.location.pathname.match(/\/notes\/\d+/)) {
                // Extract note ID from response and update URL
                const match = html.match(/\/notes\/(\d+)/);
                if (match) {
                    const noteId = match[1];
                    window.history.replaceState({}, '', '/notes/' + noteId);
                    // Update form action
                    document.getElementById('noteForm').action = '/notes/' + noteId;
                }
            }
        })
        .catch(error => {
            console.error('Auto-save error:', error);
            updateLastSaved('Error saving');
        });
    }

    function updateLastSaved(text) {
        const lastSavedElement = document.getElementById('lastSaved');
        if (lastSavedElement) {
            lastSavedElement.textContent = text;
        }
    }
})();