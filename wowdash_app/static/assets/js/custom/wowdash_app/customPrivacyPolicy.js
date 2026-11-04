// ================= Editor Initialization =================
function initQuillEditor(selector, options, initialContent) {
    const quill = new Quill(selector, options);
    if (initialContent) {
        quill.root.innerHTML = initialContent;
    }
    return quill;
}

// ================= CSRF Helper =================
function getCsrfToken() {
    const tokenElem = document.querySelector('[name=csrfmiddlewaretoken]');
    return tokenElem ? tokenElem.value : '';
}

// ================= Form Submission Handler =================
function submitPrivacyForm(content, csrfToken) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.style.display = 'none';

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;

    const contentInput = document.createElement('input');
    contentInput.type = 'hidden';
    contentInput.name = 'privacy-editor-content';
    contentInput.value = content;

    form.appendChild(csrfInput);
    form.appendChild(contentInput);
    document.body.appendChild(form);
    form.submit();
}

// ================= Cancel Handler =================
function handleCancel(contentChanged) {
    if (contentChanged) {
        if (confirm('You have unsaved changes. Are you sure you want to cancel?')) {
            window.location.reload();
        }
    } else {
        window.location.reload();
    }
}

// ================= Main Script =================
document.addEventListener('DOMContentLoaded', function () {
    const quill = initQuillEditor("#editor", {
        modules: {
            syntax: true,
            toolbar: "#toolbar-container",
        },
        placeholder: "Compose privacy policy...",
        theme: "snow",
    }, window.INITIAL_PRIVACY_CONTENT);

    let contentChanged = false;
    quill.on('text-change', function () {
        contentChanged = true;
    });

    document.getElementById('save-privacy').addEventListener('click', function () {
        if (!contentChanged) {
            console.log('No changes to save');
            return;
        }
        submitPrivacyForm(quill.root.innerHTML, getCsrfToken());
    });

    document.querySelector('.border-danger-600').addEventListener('click', function () {
        handleCancel(contentChanged);
    });
});