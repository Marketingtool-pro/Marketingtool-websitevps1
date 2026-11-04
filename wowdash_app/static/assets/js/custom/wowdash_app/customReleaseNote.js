document.addEventListener('DOMContentLoaded', function() {
    // ===============================
    // Utility Functions
    // ===============================
    function createFeatureCard(type, desc, idx) {
        const card = document.createElement('div');
        card.className = 'feature-card';
        const iconElement = document.createElement('i');
        switch(type) {
            case 'added': iconElement.className = 'ri-add-circle-line'; break;
            case 'fixed': iconElement.className = 'ri-bug-2-fill'; break;
            case 'updated': iconElement.className = 'ri-refresh-line'; break;
            case 'improved': iconElement.className = 'ri-rocket-line'; break;
        }
        const typeDiv = document.createElement('div');
        typeDiv.className = `feature-type ${type}`;
        typeDiv.appendChild(iconElement);
        const typeSpan = document.createElement('span');
        typeSpan.textContent = type;
        typeDiv.appendChild(typeSpan);
        const contentDiv = document.createElement('div');
        contentDiv.className = 'feature-content';
        contentDiv.textContent = desc;
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'feature-actions';
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn-remove';
        removeBtn.setAttribute('data-type', type);
        removeBtn.setAttribute('data-idx', idx);
        removeBtn.setAttribute('title', 'Remove');
        removeBtn.innerHTML = '<i class="ri-delete-bin-line"></i>Delete';
        actionsDiv.appendChild(removeBtn);
        card.appendChild(typeDiv);
        card.appendChild(contentDiv);
        card.appendChild(actionsDiv);
        return card;
    }
    function renderFeatures(features, featuresList, featuresJson, featuresPlaceholder) {
        featuresList.innerHTML = '';
        Object.keys(features).forEach(type => {
            features[type].forEach((desc, idx) => {
                featuresList.appendChild(createFeatureCard(type, desc, idx));
            });
        });
        featuresJson.value = JSON.stringify(features);
        featuresPlaceholder.style.display = Object.keys(features).length > 0 ? 'none' : 'block';
    }
    // ===============================
    // Feature Add/Remove Logic
    // ===============================
    const featureType = document.getElementById('feature-type');
    const featureDesc = document.getElementById('feature-desc');
    const addFeatureBtn = document.getElementById('add-feature-btn');
    const featuresList = document.getElementById('features-list');
    const featuresJson = document.getElementById('features-json');
    const featuresPlaceholder = document.getElementById('features-placeholder');
    const releaseNoteForm = document.getElementById('release-note-form');
    let features = {};

    addFeatureBtn.addEventListener('click', function() {
        const type = featureType.value;
        const desc = featureDesc.value.trim();
        if (!desc) {
            alert('Please enter a feature description');
            return;
        }
        if (!features[type]) features[type] = [];
        if (features[type].includes(desc)) {
            alert('This feature has already been added');
            return;
        }
        features[type].push(desc);
        renderFeatures(features, featuresList, featuresJson, featuresPlaceholder);
        featureDesc.value = '';
        featureDesc.focus();
    });

    featureDesc.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addFeatureBtn.click();
        }
    });

    featuresList.addEventListener('click', function(e) {
        if (e.target.closest('button')) {
            const btn = e.target.closest('button');
            const type = btn.getAttribute('data-type');
            const idx = parseInt(btn.getAttribute('data-idx'));
            features[type].splice(idx, 1);
            if (features[type].length === 0) delete features[type];
            renderFeatures(features, featuresList, featuresJson, featuresPlaceholder);
        }
    });

    // ===============================
    // Form Submission Handler
    // ===============================
    releaseNoteForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const version = this.querySelector('[name="version"]').value.trim();
        const releaseDate = this.querySelector('[name="release_date"]').value;
        const heading = this.querySelector('[name="heading"]').value.trim();
        if (!version) { alert('Please enter a version'); return; }
        if (!releaseDate) { alert('Please select a release date'); return; }
        if (!heading) { alert('Please enter a heading'); return; }
        if (Object.keys(features).length === 0) { alert('Please add at least one feature'); return; }
        featuresJson.value = JSON.stringify(features);
        this.submit();
    });
});