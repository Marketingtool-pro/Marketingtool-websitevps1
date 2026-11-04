document.addEventListener('DOMContentLoaded', function() {
    // ===============================
    // Utility Functions
    // ===============================
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
    function showModal(modal) {
        modal.classList.remove('hidden');
    }
    function hideModal(modal, form, message) {
        modal.classList.add('hidden');
        if (form) form.reset();
        if (message) message.textContent = '';
        currentEditForm = null;
    }
    function handleAjaxResponse(data, onSuccess, onError) {
        if (data.success) {
            if (typeof onSuccess === 'function') onSuccess();
        } else {
            if (typeof onError === 'function') onError(data.error || 'Operation failed.');
        }
    }

    // ===============================
    // Modal Handling
    // ===============================
    const addTeamBtn = document.getElementById('add-team-btn');
    const addTeamModal = document.getElementById('add-team-modal');
    const closeTeamModal = document.getElementById('close-team-modal');
    const cancelTeamBtn = document.getElementById('cancel-team-btn');
    const addTeamForm = document.getElementById('add-team-form');
    const addTeamMessage = document.getElementById('add-team-message');

    addTeamBtn.addEventListener('click', () => {
        if (currentEditForm) {
            const modal = document.getElementById('add-team-modal');
            modal.querySelector('h3').textContent = 'Add New Team Member';
            const submitBtn = modal.querySelector('button[type="submit"]');
            submitBtn.textContent = 'Add Member';
            const oldForm = modal.querySelector('form');
            oldForm.parentNode.replaceChild(addTeamForm, oldForm);
            currentEditForm = null;
        }
        showModal(addTeamModal);
    });
    
    closeTeamModal.addEventListener('click', () => {
        hideModal(addTeamModal, currentEditForm || addTeamForm, addTeamMessage);
    });
    
    cancelTeamBtn.addEventListener('click', () => {
        hideModal(addTeamModal, currentEditForm || addTeamForm, addTeamMessage);
    });

    // ===============================
    // Add Team Member
    // ===============================
    function resetAddForm() {
        const modal = document.getElementById('add-team-modal');
        modal.querySelector('h3').textContent = 'Add New Team Member';
        const submitBtn = modal.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Add Member';
    }

    addTeamForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(addTeamForm);
        formData.set('featured', addTeamForm.featured.checked ? 'true' : 'false');
        fetch('/aiwave/admin/team/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => handleAjaxResponse(data, () => {
            addTeamMessage.textContent = 'Team member added successfully!';
            addTeamMessage.classList.add('text-green-600');
            setTimeout(() => {
                hideModal(addTeamModal, addTeamForm, addTeamMessage);
                resetAddForm();
                window.location.reload();
            }, 1000);
        }, (err) => {
            addTeamMessage.textContent = err;
            addTeamMessage.classList.add('text-red-600');
        }))
        .catch(() => {
            addTeamMessage.textContent = 'An error occurred.';
            addTeamMessage.classList.add('text-red-600');
        });
    });

    // ===============================
    // Edit Team Member
    // ===============================
    let currentEditForm = null;
    let originalForm = null;
    
    function setupEditForm(btn) {
        if (currentEditForm) return null; // Return null if already editing
        
        const memberId = btn.getAttribute('data-member-id');
        const memberName = btn.getAttribute('data-name');
        const memberPosition = btn.getAttribute('data-position');
        const memberOrder = btn.getAttribute('data-order');
        const memberPhotoUrl = btn.getAttribute('data-photo-url');
        const memberFeatured = btn.getAttribute('data-featured') === 'true';
        
        // Store the original form if not already stored
        if (!originalForm) {
            originalForm = document.getElementById('add-team-form');
        }
        
        // Clone the add form and update it for editing
        const editForm = originalForm.cloneNode(true);
        editForm.id = 'edit-team-form';
        
        // Update form fields
        editForm.querySelector('[name="name"]').value = memberName;
        editForm.querySelector('[name="position"]').value = memberPosition;
        editForm.querySelector('[name="order"]').value = memberOrder;
        editForm.querySelector('[name="featured"]').checked = memberFeatured;
        
        // Make photo field not required for editing
        const photoInput = editForm.querySelector('[name="photo"]');
        photoInput.required = false;
        
        // Show current photo if exists
        if (memberPhotoUrl) {
            const photoPreview = document.createElement('div');
            photoPreview.className = 'mb-3';
            photoPreview.innerHTML = `
                <p class='text-sm text-gray-600 dark:text-gray-300 mb-1'>Current Photo:</p>
                <img src="${memberPhotoUrl}" alt="Current photo" class="max-h-20 rounded">
                <p class='text-xs text-gray-500 mt-1'>Leave blank to keep current photo</p>
            `;
            photoInput.parentNode.insertBefore(photoPreview, photoInput);
        }
        
        // Update form submission
        editForm.onsubmit = function(e) {
            e.preventDefault();
            const formData = new FormData(editForm);
            formData.set('featured', editForm.featured.checked ? 'true' : 'false');
            
            // Only include photo if a new one is selected
            if (!formData.get('photo').name) {
                formData.delete('photo');
            }
            
            const submitBtn = editForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="ri-loader-4-line animate-spin"></i> Updating...';
            
            fetch(`/aiwave/admin/team/${memberId}/edit/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    alert(data.alert?.message || 'Failed to update team member');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Update Member';
                }
            })
            .catch(() => {
                alert('An error occurred while updating the team member');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Update Member';
            });
        };
        
        return editForm;
    }
    
    function showEditModal(editForm) {
        if (!editForm) return;
        
        const modal = document.getElementById('add-team-modal');
        modal.querySelector('h3').textContent = 'Edit Team Member';
        const submitBtn = modal.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Update Member';
        
        // Replace form in modal
        const oldForm = modal.querySelector('form');
        oldForm.parentNode.replaceChild(editForm, oldForm);
        
        // Update close handlers
        const closeModal = () => {
            if (originalForm) {
                const currentForm = modal.querySelector('form');
                if (currentForm) {
                    currentForm.parentNode.replaceChild(originalForm, currentForm);
                }
                originalForm = null;
            }
            modal.classList.add('hidden');
            currentEditForm = null;
            modal.removeEventListener('click', handleModalClick);
        };
        
        const handleModalClick = (e) => {
            if (e.target === modal) {
                closeModal();
            }
        };
        
        modal.addEventListener('click', handleModalClick);
        
        // Store close function for external access
        editForm.closeModal = closeModal;
        
        // Show modal
        modal.classList.remove('hidden');
        currentEditForm = editForm;
    }
    
    // Handle edit button clicks
    document.addEventListener('click', function(e) {
        const editBtn = e.target.closest('.edit-member-btn');
        if (editBtn) {
            e.preventDefault();
            if (currentEditForm) {
                // If already editing, close current form first
                if (typeof currentEditForm.closeModal === 'function') {
                    currentEditForm.closeModal();
                }
                // Small delay to allow modal to close
                setTimeout(() => {
                    const newEditForm = setupEditForm(editBtn);
                    showEditModal(newEditForm);
                }, 100);
            } else {
                const newEditForm = setupEditForm(editBtn);
                showEditModal(newEditForm);
            }
        }
    });

    // ===============================
    // Delete Team Member
    // ===============================
    document.querySelectorAll('.delete-member-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const memberId = this.getAttribute('data-member-id');
            if (confirm('Are you sure you want to delete this team member?')) {
                fetch(`/aiwave/admin/team/${memberId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => handleAjaxResponse(data, () => {
                    const card = document.querySelector(`.team-member-card[data-member-id="${memberId}"]`);
                    card.remove();
                }, (err) => alert(err)))
                .catch(() => {
                    alert('An error occurred while deleting team member.');
                });
            }
        });
    });

    // ===============================
    // Toggle Featured Status
    // ===============================
    document.querySelectorAll('.toggle-featured-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const memberId = this.getAttribute('data-member-id');
            const currentState = this.getAttribute('data-featured') === 'true';
            const newState = !currentState;
            const formData = new FormData();
            formData.append('action', 'toggle_featured');
            formData.append('featured', newState.toString());
            // Include existing member data
            const memberName = this.getAttribute('data-member-name');
            const memberPosition = this.getAttribute('data-member-position');
            const memberOrder = this.getAttribute('data-member-order') || '0';
            formData.append('name', memberName);
            formData.append('position', memberPosition);
            formData.append('order', memberOrder);
            fetch(`/aiwave/admin/team/${memberId}/toggle-featured/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    // Handle 400 or other error responses
                    if (data.alert && data.alert.message) {
                        alert(data.alert.message);
                    } else {
                        alert('An error occurred while updating featured status.');
                    }
                    return;
                }
                
                // Handle successful response
                if (data.success) {
                    this.setAttribute('data-featured', newState.toString());
                    this.classList.remove('btn-success', 'btn-warning');
                    this.classList.add(newState ? 'btn-success' : 'btn-warning');
                    const icon = this.querySelector('i');
                    icon.className = `ri-${newState ? 'star-fill' : 'star-line'}`;
                    this.title = newState ? 'Unfeature' : 'Feature';
                    
                    if (data.alert && data.alert.message) {
                        alert(data.alert.message);
                    }
                }
            })
            .catch(() => {
                alert('An error occurred while updating featured status.');
            });
        });
    });
});