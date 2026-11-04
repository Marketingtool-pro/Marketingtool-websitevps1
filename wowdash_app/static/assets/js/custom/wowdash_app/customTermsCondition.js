// ===============================
// Utility Functions
// ===============================
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function createHiddenInput(name, value) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = value;
    return input;
}

// ===============================
// Quill Editor Setup & Handlers
// ===============================
const quill = new Quill("#editor", {
    modules: {
        syntax: true,
        toolbar: "#toolbar-container",
    },
    placeholder: "Compose terms and conditions...",
    theme: "snow",
});

// Set initial content from a global variable set in the template
if (window.INITIAL_TERMS_CONTENT) {
    quill.root.innerHTML = window.INITIAL_TERMS_CONTENT;
}

let contentChanged = false;
quill.on('text-change', function () {
    contentChanged = true;
});

// ===============================
// Save & Cancel Handlers
// ===============================
document.getElementById('save-terms').addEventListener('click', function () {
    if (!contentChanged) {
        console.log('No changes to save');
        return;
    }
    const content = quill.root.innerHTML;
    const form = document.createElement('form');
    form.method = 'POST';
    form.style.display = 'none';
    form.appendChild(createHiddenInput('csrfmiddlewaretoken', getCSRFToken()));
    form.appendChild(createHiddenInput('terms-editor-content', content));
    document.body.appendChild(form);
    form.submit();
});

document.querySelector('.border-danger-600').addEventListener('click', function () {
    if (contentChanged) {
        if (confirm('You have unsaved changes. Are you sure you want to cancel?')) {
            window.location.reload();
        }
    } else {
        window.location.reload();
    }
});