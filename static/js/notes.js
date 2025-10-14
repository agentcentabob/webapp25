// notes.js - with autosave and image upload
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
            console.error('easymde library not loaded.');
            alert('editor library failed to load. please refresh the page.');
            return;
        }
        
        easyMDE = new EasyMDE({
            element: document.getElementById('noteContent'),
            spellChecker: false,
            autofocus: true,
            placeholder: "start typing your note... markdown is supported!\n\n# heading 1\n## heading 2\n**bold** and *italic*\n- list item\n\n[link](url)",
            status: false,
            toolbar: [
                "bold", "italic", "heading", "|",
                "quote", "unordered-list", "ordered-list", "|",
                "link", 
                {
                    name: "image",
                    action: openImageUpload,
                    className: "fa fa-image",
                    title: "upload image"
                },
                "|",
                "preview", "side-by-side", "fullscreen", "|",
                "guide"
            ],
            minHeight: "500px",
            renderingConfig: {
                singleLineBreaks: false,
                codeSyntaxHighlighting: true,
            }
        });

        // autosave on content change after 2 seconds without typing
        easyMDE.codemirror.on("change", function() {
            hasChanges = true;
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                autoSave();
            }, 2000);
        });

        // autosave on title change after 2 seconds without typing
        const titleInput = document.getElementById('noteTitle');
        if (titleInput) {
            titleInput.addEventListener('input', () => {
                hasChanges = true;
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(() => {
                    autoSave();
                }, 2000);
            });
        }

        // autosave on address change
        const addressInput = document.getElementById('noteAddress');
        if (addressInput) {
            addressInput.addEventListener('input', () => {
                hasChanges = true;
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(() => {
                    autoSave();
                }, 2000);
            });
        }

        // delete button
        const deleteBtn = document.getElementById('deleteBtn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                if (confirm('are you sure you want to delete this note?')) {
                    document.getElementById('deleteForm').submit();
                }
            });
        }

        // before form submission, sync easymde content to textarea
        const form = document.getElementById('noteForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                const textarea = document.getElementById('noteContent');
                textarea.value = easyMDE.value();
            });
        }

        // setup drag and drop on editor
        setupEditorDragDrop();
    }

    function autoSave() {
        if (!hasChanges) return;
        
        // sync easymde content to textarea
        const textarea = document.getElementById('noteContent');
        textarea.value = easyMDE.value();
        
        const form = document.getElementById('noteForm');
        const formData = new FormData(form);
        
        // submit form via fetch without reloading page
        fetch(form.action || window.location.href, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                updateLastSaved('auto-saved at ' + new Date().toLocaleTimeString());
                hasChanges = false;
                
                // if this was a new note, update url to point to the note
                return response.text();
            } else {
                updateLastSaved('error saving');
            }
        })
        .then(html => {
            // check if we were redirected (new note created)
            if (html && html.includes('/notes/') && !window.location.pathname.match(/\/notes\/\d+/)) {
                // extract note id from response and update url
                const match = html.match(/\/notes\/(\d+)/);
                if (match) {
                    const noteId = match[1];
                    window.history.replaceState({}, '', '/notes/' + noteId);
                    // update form action
                    document.getElementById('noteForm').action = '/notes/' + noteId;
                }
            }
        })
        .catch(error => {
            console.error('auto-save error:', error);
            updateLastSaved('error saving');
        });
    }

    function updateLastSaved(text) {
        const lastSavedElement = document.getElementById('lastSaved');
        if (lastSavedElement) {
            lastSavedElement.textContent = text;
        }
    }

    // image upload - triggered from toolbar button
    function openImageUpload() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.addEventListener('change', (e) => {
            handleImageUpload(e.target.files[0]);
        });
        input.click();
    }

    // handle image upload
    async function handleImageUpload(file) {
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload-image', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // insert markdown image into editor
                const imageMarkdown = `\n![${file.name}](${data.url})\n`;
                easyMDE.value(easyMDE.value() + imageMarkdown);
                hasChanges = true;
                
                // trigger autosave immediately
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(() => {
                    autoSave();
                }, 500);
            } else {
                alert('upload failed: ' + data.error);
            }
        } catch (error) {
            console.error('upload error:', error);
            alert('upload failed');
        }
    }

    // drag and drop on editor
    function setupEditorDragDrop() {
        const editorBody = document.getElementById('editorBody');
        if (!editorBody) return;
        
        editorBody.addEventListener('dragover', (e) => {
            e.preventDefault();
            editorBody.style.borderColor = '#4CAF50';
            editorBody.style.backgroundColor = 'rgba(76, 175, 80, 0.05)';
        });
        
        editorBody.addEventListener('dragleave', () => {
            editorBody.style.borderColor = '';
            editorBody.style.backgroundColor = '';
        });
        
        editorBody.addEventListener('drop', (e) => {
            e.preventDefault();
            editorBody.style.borderColor = '';
            editorBody.style.backgroundColor = '';
            
            const files = e.dataTransfer.files;
            for (let file of files) {
                if (file.type.startsWith('image/')) {
                    handleImageUpload(file);
                }
            }
        });
    }
})();