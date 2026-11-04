document.addEventListener('DOMContentLoaded', function() {
    // Image preview functionality
    const imageInput = document.getElementById('featured_image');
    const imagePreview = document.getElementById('image-preview');
    
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.style.display = 'block';
                const img = new Image();
                img.onload = function() {
                    // If image is larger than 800px wide, scale it down
                    if (this.width > 800) {
                        this.style.maxWidth = '800px';
                    }
                };
                img.src = e.target.result;
                img.alt = 'Preview';
                imagePreview.innerHTML = '';
                imagePreview.appendChild(img);
            };
            reader.readAsDataURL(file);
        }
    });

    // Preview button functionality
    document.getElementById('preview-button').addEventListener('click', function() {
        const title = document.getElementById('title').value;
        const excerpt = document.getElementById('excerpt').value;
        const content = document.getElementById('content').value;
        const category = document.getElementById('category').value;
        const tags = document.getElementById('tags').value;
        const featuredImage = document.getElementById('featured_image').files[0];

        if (!title || !excerpt || !content || !category || !featuredImage) {
            alert('Please fill in all required fields before previewing.');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            const modal = document.createElement('div');
            modal.className = 'preview-modal';
            const previewContent = document.createElement('div');
            previewContent.className = 'preview-content';
            const addText = (parent, tagName, className, text) => {
                const el = document.createElement(tagName);
                if (className) el.className = className;
                el.textContent = text;
                parent.appendChild(el);
                return el;
            };
            const previewImg = document.createElement('img');
            previewImg.src = URL.createObjectURL(new Blob([featuredImage], { type: featuredImage.type }));
            previewImg.alt = title;
            previewContent.appendChild(previewImg);
            addText(previewContent, 'h2', '', title);
            addText(previewContent, 'p', 'excerpt', excerpt);
            addText(previewContent, 'div', 'content', content).style.whiteSpace = 'pre-wrap';
            const meta = document.createElement('div');
            meta.className = 'meta';
            addText(meta, 'span', 'category', category);
            if (tags) addText(meta, 'span', 'tags', tags);
            previewContent.appendChild(meta);
            const closeBtn = addText(previewContent, 'button', 'btn-default btn-border btn-opacity', 'Close Preview');
            closeBtn.addEventListener('click', () => modal.remove());
            modal.appendChild(previewContent);
            document.body.appendChild(modal);
        };
        reader.readAsDataURL(featuredImage);
    });

    // Category autocomplete
    const categoryInput = document.getElementById('category');
    const categorySuggestions = document.getElementById('category-suggestions');
    const existingCategories = ['AI', 'Machine Learning', 'Technology', 'Programming', 'Data Science', 'Web Development', 'Mobile Development', 'Cloud Computing', 'Cybersecurity', 'Blockchain'];

    categoryInput.addEventListener('input', function() {
        const value = this.value.toLowerCase();
        if (value.length < 1) {
            categorySuggestions.style.display = 'none';
            return;
        }

        const matches = existingCategories.filter(category => 
            category.toLowerCase().includes(value)
        );

        if (matches.length > 0) {
            categorySuggestions.innerHTML = matches
                .map(category => `<div class="suggestion-item">${category}</div>`)
                .join('');
            categorySuggestions.style.display = 'block';
        } else {
            categorySuggestions.style.display = 'none';
        }
    });

    categorySuggestions.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-item')) {
            categoryInput.value = e.target.textContent;
            categorySuggestions.style.display = 'none';
        }
    });

    // Tags autocomplete
    const tagsInput = document.getElementById('tags');
    const tagSuggestions = document.getElementById('tag-suggestions');
    const selectedTags = document.getElementById('selected-tags');
    const existingTags = ['python', 'javascript', 'react', 'nodejs', 'django', 'flask', 'aws', 'azure', 'docker', 'kubernetes', 'ai', 'ml', 'data-science', 'web-development', 'mobile-development'];
    let currentTags = [];

    tagsInput.addEventListener('input', function() {
        const value = this.value.toLowerCase();
        if (value.length < 1) {
            tagSuggestions.style.display = 'none';
            return;
        }

        const matches = existingTags.filter(tag => 
            tag.toLowerCase().includes(value) && !currentTags.includes(tag)
        );

        if (matches.length > 0) {
            tagSuggestions.innerHTML = matches
                .map(tag => `<div class="suggestion-item">${tag}</div>`)
                .join('');
            tagSuggestions.style.display = 'block';
        } else {
            tagSuggestions.style.display = 'none';
        }
    });

    tagSuggestions.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-item')) {
            const tag = e.target.textContent;
            if (!currentTags.includes(tag)) {
                currentTags.push(tag);
                updateSelectedTags();
                tagsInput.value = '';
                tagSuggestions.style.display = 'none';
            }
        }
    });

    function updateSelectedTags() {
        selectedTags.textContent = '';
        currentTags.forEach(tag => {
            const item = document.createElement('div');
            item.className = 'tag-item';
            item.append(document.createTextNode(tag + ' '));
            const remove = document.createElement('span');
            remove.className = 'remove-tag';
            remove.dataset.tag = tag;
            remove.innerHTML = '&times;';
            item.appendChild(remove);
            selectedTags.appendChild(item);
        });
        
        // Update hidden input with comma-separated tags
        tagsInput.value = currentTags.join(', ');
    }

    selectedTags.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-tag')) {
            const tag = e.target.dataset.tag;
            currentTags = currentTags.filter(t => t !== tag);
            updateSelectedTags();
        }
    });

    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.autocomplete-container')) {
            categorySuggestions.style.display = 'none';
            tagSuggestions.style.display = 'none';
        }
    });
});
