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

function hideMessageDetails() {
    document.getElementById('messageDetails').style.display = 'none';
}

function updateMessageDetails(data) {
    document.getElementById('detailName').textContent = data.name;
    document.getElementById('detailEmail').textContent = data.email;
    document.getElementById('detailPhone').textContent = data.phone;
    document.getElementById('detailSubject').textContent = data.subject;
    document.getElementById('detailMessage').textContent = data.message;
    document.getElementById('detailDate').textContent = data.date;
}

function updateToggleReadButton(isRead) {
    const toggleBtn = document.querySelector('.toggle-read-btn');
    const label = toggleBtn.querySelector('.toggle-read-label');
    if (isRead) {
        label.textContent = 'Mark as Unread';
        toggleBtn.classList.remove('btn-primary');
        toggleBtn.classList.add('btn-warning');
    } else {
        label.textContent = 'Mark as Read';
        toggleBtn.classList.remove('btn-warning');
        toggleBtn.classList.add('btn-primary');
    }
    toggleBtn.classList.remove('d-none');
}

function removeRowWithAnimation(row, callback) {
    row.style.transition = 'all 0.3s ease';
    row.style.opacity = '0';
    row.style.transform = 'translateX(-100%)';
    setTimeout(() => {
        row.remove();
        if (typeof callback === 'function') callback();
    }, 300);
}


document.addEventListener('DOMContentLoaded', function() {
    // Delegate for view message buttons
    document.querySelectorAll('.view-message').forEach(button => {
        button.addEventListener('click', function() {
            // Populate message details
            updateMessageDetails({
                name: this.dataset.name,
                email: this.dataset.email,
                phone: this.dataset.phone,
                subject: this.dataset.subject,
                message: this.dataset.message,
                date: this.dataset.date
            });
            // Store query ID and row reference
            const messageDetails = document.getElementById('messageDetails');
            messageDetails.dataset.queryId = this.dataset.queryId;
            messageDetails.dataset.rowId = this.closest('tr').id;
            // Show message details section
            messageDetails.style.display = 'block';
            // Scroll to top smoothly
            window.scrollTo({ top: 0, behavior: 'smooth' });
            // Mark as read if not already
            const row = document.getElementById(messageDetails.dataset.rowId);
            const isRead = !row.classList.contains('bg-light-blue');
            if (!isRead) {
                fetch(`/aiwave/admin/toggle-query-read/${this.dataset.queryId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.is_read) {
                        row.classList.remove('bg-light-blue');
                        row.querySelector('td:nth-last-child(2)').innerHTML = '<span class="badge bg-secondary">Read</span>';
                        updateToggleReadButton(true);
                    }
                });
            } else {
                updateToggleReadButton(true);
            }
        });
    });

    // Toggle Read/Unread Handler
    document.querySelector('.toggle-read-btn').addEventListener('click', function() {
        const messageDetails = document.getElementById('messageDetails');
        const queryId = messageDetails.dataset.queryId;
        const rowId = messageDetails.dataset.rowId;
        const row = document.getElementById(rowId);
        fetch(`/aiwave/admin/toggle-query-read/${queryId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.is_read) {
                    row.classList.remove('bg-light-blue');
                    row.querySelector('td:nth-last-child(2)').innerHTML = '<span class="badge bg-secondary">Read</span>';
                } else {
                    row.classList.add('bg-light-blue');
                    row.querySelector('td:nth-last-child(2)').innerHTML = '<span class="badge bg-primary">Unread</span>';
                }
                updateToggleReadButton(data.is_read);
            } else {
                alert('Error toggling read status');
            }
        });
    });

    // Delete Handler
    document.querySelector('.delete-btn').addEventListener('click', function() {
        if (confirm('Are you sure you want to delete this message?')) {
            const messageDetails = document.getElementById('messageDetails');
            const queryId = messageDetails.dataset.queryId;
            const rowId = messageDetails.dataset.rowId;
            const row = document.getElementById(rowId);
            fetch(`/aiwave/admin/delete-query/${queryId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    removeRowWithAnimation(row, function() {
                        hideMessageDetails();
                        // Check if table is empty
                        const tbody = document.querySelector('table tbody');
                        if (tbody.children.length === 0) {
                            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No inquiries found</td></tr>';
                        }
                    });
                } else {
                    alert('Error deleting message');
                }
            })
            .catch(error => {
                alert('Error deleting message');
            });
        }
    });
});