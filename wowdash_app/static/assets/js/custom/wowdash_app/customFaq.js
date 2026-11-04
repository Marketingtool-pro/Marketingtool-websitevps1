// ================= CSRF Helper =================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ================= Modal Handlers =================
function openFaqModal(form, modal) {
    document.querySelector('#add-faq-modal h3').classList.remove('hidden');
    form.reset();
    form.removeAttribute('data-edit-id');
    modal.classList.remove('hidden');
}
function closeFaqModal(modal) {
    modal.classList.add('hidden');
}

// ================= AJAX Helpers =================
function ajaxPost(url, formData, onSuccess, onError) {
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(onSuccess)
    .catch(onError);
}
function ajaxPostJson(url, data, onSuccess, onError) {
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(onSuccess)
    .catch(onError);
}

// ================= Main Script =================
document.addEventListener('DOMContentLoaded', function() {
    // Modal open/close logic
    const addFaqBtn = document.getElementById('add-faq-btn');
    const addFaqModal = document.getElementById('add-faq-modal');
    const closeFaqModalBtn = document.getElementById('close-faq-modal');
    const cancelFaqBtn = document.getElementById('cancel-faq-btn');
    const addFaqForm = document.getElementById('add-faq-form');
    const addFaqMessage = document.getElementById('add-faq-message');

    addFaqBtn.addEventListener('click', () => openFaqModal(addFaqForm, addFaqModal));
    closeFaqModalBtn.addEventListener('click', () => closeFaqModal(addFaqModal));
    cancelFaqBtn.addEventListener('click', () => closeFaqModal(addFaqModal));

    // AJAX form submit
    addFaqForm.addEventListener('submit', function(e) {
        e.preventDefault();
        addFaqMessage.textContent = '';
        const formData = new FormData(addFaqForm);
        formData.set('is_active', addFaqForm.is_active.checked ? 'true' : 'false');
        let url = '/aiwave/admin/faqs/create/';
        const editId = addFaqForm.getAttribute('data-edit-id');
        if (editId) {
            url = `/aiwave/admin/faqs/${editId}/edit/`;
        }
        ajaxPost(url, formData, function(data) {
            if (data.success) {
                addFaqMessage.textContent = editId ? 'FAQ updated successfully!' : 'FAQ added successfully!';
                addFaqMessage.classList.add('text-green-600');
                setTimeout(() => {
                    closeFaqModal(addFaqModal);
                    addFaqForm.reset();
                    addFaqMessage.textContent = '';
                    if (data.next_order) {
                        addFaqForm.order.value = data.next_order;
                    }
                    window.location.reload();
                }, 1000);
            } else {
                addFaqMessage.textContent = data.error || 'Failed to save FAQ.';
                addFaqMessage.classList.add('text-red-600');
            }
        }, function() {
            addFaqMessage.textContent = 'An error occurred.';
            addFaqMessage.classList.add('text-red-600');
        });
    });

    // Edit FAQ logic
    document.querySelectorAll('.edit-faq-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector('#add-faq-modal h3').classList.add('hidden');
            addFaqForm.category.value = btn.getAttribute('data-faq-category');
            addFaqForm.question.value = btn.getAttribute('data-faq-question');
            addFaqForm.answer.value = btn.getAttribute('data-faq-answer');
            addFaqForm.is_active.checked = btn.getAttribute('data-faq-is_active') === 'true';
            addFaqForm.setAttribute('data-edit-id', btn.getAttribute('data-faq-id'));
            addFaqModal.classList.remove('hidden');
        });
    });

    // Delete FAQ logic
    document.querySelectorAll('.delete-faq-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const faqId = btn.getAttribute('data-faq-id');
            if (confirm('Are you sure you want to delete this FAQ?')) {
                ajaxPost(`/aiwave/admin/faqs/${faqId}/delete/`, null, function(data) {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert(data.error || 'Failed to delete FAQ.');
                    }
                }, function() {
                    alert('An error occurred while deleting FAQ.');
                });
            }
        });
    });

    // Toggle FAQ visibility logic
    document.querySelectorAll('.toggle-faq-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const faqId = btn.getAttribute('data-faq-id');
            const currentState = btn.getAttribute('data-faq-is_active') === 'true';
            const newState = !currentState;
            ajaxPostJson(`/aiwave/admin/faqs/${faqId}/toggle-visibility/`, {is_active: newState}, function(data) {
                if (data.success) {
                    btn.setAttribute('data-faq-is_active', newState.toString());
                    btn.classList.remove('btn-success', 'btn-warning');
                    btn.classList.add(newState ? 'btn-success' : 'btn-warning');
                    const icon = btn.querySelector('i');
                    icon.className = `ri-${newState ? 'eye-line' : 'eye-off-line'}`;
                    btn.title = newState ? 'Hide FAQ' : 'Show FAQ';
                    btn.querySelector('.sr-only').textContent = newState ? 'Hide' : 'Show';
                } else {
                    alert(data.error || 'Failed to toggle FAQ visibility.');
                }
            }, function() {
                alert('An error occurred while toggling FAQ visibility.');
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('#vertical-tab button[role="tab"]');
    const tabPanels = document.querySelectorAll('#vertical-tab-content > div[role="tabpanel"]');

    // On page load: show only the first panel, set only the first button as selected and active
    tabPanels.forEach((panel, idx) => {
        if (idx === 0) {
            panel.classList.remove('hidden');
            panel.style.display = 'block';
        } else {
            panel.classList.add('hidden');
            panel.style.display = 'none';
        }
    });
    tabButtons.forEach((btn, idx) => {
        btn.setAttribute('aria-selected', idx === 0 ? 'true' : 'false');
        if (idx === 0) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    tabButtons.forEach((btn, idx) => {
        btn.addEventListener('click', function() {
            // Hide all panels and set all buttons to not selected and not active
            tabPanels.forEach(panel => {
                panel.classList.add('hidden');
                panel.style.display = 'none';
            });
            tabButtons.forEach(b => {
                b.setAttribute('aria-selected', 'false');
                b.classList.remove('active');
            });

            // Show the selected panel and set button as selected and active
            const target = btn.getAttribute('data-tabs-target');
            const targetPanel = document.querySelector(target);
            if (targetPanel) {
                targetPanel.classList.remove('hidden');
                targetPanel.style.display = 'block';
            }
            btn.setAttribute('aria-selected', 'true');
            btn.classList.add('active');
        });
    });
});