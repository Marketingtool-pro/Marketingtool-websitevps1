// Debounce function to prevent too many API calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Simple CSRF helper
function getCSRFToken() {
    // Try to get from meta tag
    const metaToken = document.querySelector('meta[name=csrf-token]') || 
                     document.querySelector('[name=csrfmiddlewaretoken]');
    return metaToken ? (metaToken.content || metaToken.value) : '';
}

// ======================== User Table Helpers =====================
function renderUserRow(user, index, isFiltered = false) {
    const statusClass = user.status === 'Active'
        ? 'bg-success-100 dark:bg-success-600/25 text-success-600 dark:text-success-400 border border-success-600'
        : 'bg-danger-100 dark:bg-danger-600/25 text-danger-600 dark:text-danger-400 border border-danger-600';
    
    // Calculate the correct serial number
    let serialNumber;
    if (isFiltered) {
        // For filtered results, start from 1
        serialNumber = index + 1;
    } else {
        // For paginated results, calculate based on page and items per page
        const perPage = parseInt($('.per-page-select').val()) || 10;
        serialNumber = ((window.currentPage - 1) * perPage) + index + 1;
    }
    
    return `
        <tr>
            <td style="max-width:60px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                <div class="flex items-center gap-2">
                    <div class="form-check style-check flex items-center">
                        <input class="form-check-input rounded border border-neutral-400" type="checkbox" name="checkbox" id="SL-${user.id}">
                    </div>
                    ${String(serialNumber).padStart(2, '0')}
                </div>
            </td>
            <td style="max-width:110px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${user.join_date}</td>
            <td style="max-width:140px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                <div class="flex items-center">
                    <img src="${user.profile_picture || window.DEFAULT_PROFILE_IMG}" alt=""
                        class="w-10 h-10 rounded-full shrink-0 me-2 overflow-hidden">
                    <div class="grow">
                        <span class="text-base mb-0 font-normal text-secondary-light text-truncate" style="max-width:90px; display:inline-block;">${user.name}</span>
                    </div>
                </div>
            </td>
            <td style="max-width:180px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                <span class="text-base mb-0 font-normal text-secondary-light text-truncate" style="max-width:160px; display:inline-block;">${user.email}</span>
            </td>
            <td style="max-width:120px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${user.department}</td>
            <td style="max-width:120px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${user.designation}</td>
            <td class="text-center" style="max-width:120px; white-space:nowrap; overflow:visible;">
                ${user.is_superuser ?
                    `<span class="bg-success-100 dark:bg-success-600/25 text-success-600 dark:text-success-400 border border-success-600 px-4 py-1.5 rounded font-medium text-sm" style="min-width:80px; display:inline-block;">Active</span>` :
                    `<button type="button" 
                        class="toggle-status-btn ${statusClass} px-4 py-1.5 rounded font-medium text-sm cursor-pointer hover:opacity-80 transition-opacity"
                        style="min-width:80px; white-space:nowrap; display:inline-block; overflow:visible;"
                        data-user-id="${user.id}"
                        data-csrf-token="{{ csrf_token }}">
                        ${user.status}
                    </button>`
                }
            </td>
            <td class="text-center" style="max-width:80px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                ${!user.is_superuser ? `
                    <div class="flex items-center gap-2 justify-center">
                        <button type="button"
                            class="remove-item-btn bg-danger-100 dark:bg-danger-600/25 hover:bg-danger-200 text-danger-600 dark:text-danger-500 font-medium px-3 py-1.5 rounded-full text-sm transition-all duration-200"
                            data-user-id="${user.id}"
                            data-csrf-token="{{ csrf_token }}"
                            data-confirming="false">
                            <iconify-icon icon="fluent:delete-24-regular" class="menu-icon"></iconify-icon>
                        </button>
                    </div>
                ` : ''}
            </td>
        </tr>
    `;
}

function renderEmptyState() {
    return `
        <tr>
            <td colspan="8" class="text-center py-4">
                <span class="text-base mb-0 font-normal text-secondary-light">No users found</span>
            </td>
        </tr>
    `;
}

function filterUsers(users) {
    const searchTerm = $('input[name="table-search"]').val().toLowerCase();
    const statusFilter = $('select:eq(1)').val();
    if (!searchTerm && statusFilter === 'Status') {
        return users;
    }
    return users.filter(user => {
        const matchesSearch = !searchTerm ||
            user.name.toLowerCase().includes(searchTerm) ||
            user.email.toLowerCase().includes(searchTerm) ||
            user.department.toLowerCase().includes(searchTerm) ||
            user.designation.toLowerCase().includes(searchTerm) ||
            user.join_date.toLowerCase().includes(searchTerm) ||
            user.status.toLowerCase().includes(searchTerm) ||
            String(user.id).includes(searchTerm);
        const matchesStatus = statusFilter === 'Status' ||
            (statusFilter === 'Active' && user.status === 'Active') ||
            (statusFilter === 'Inactive' && user.status === 'Inactive');
        return matchesSearch && matchesStatus;
    });
}

function updatePagination(data) {
    window.totalPages = data.total_pages;
    window.currentPage = data.current_page;
    const pagination = $('.pagination');
    pagination.empty();
    
    // Previous button (only show if not on first page)
    if (window.currentPage > 1) {
        pagination.append(`
            <li class="page-item">
                <a class="page-link bg-neutral-300 dark:bg-neutral-600 text-secondary-light font-semibold rounded-lg border-0 flex items-center justify-center h-8 w-8 text-base hover:bg-neutral-400 dark:hover:bg-neutral-500"
                    href="javascript:void(0)" data-page="${window.currentPage - 1}">
                    <iconify-icon icon="ep:d-arrow-left"></iconify-icon>
                </a>
            </li>
        `);
    }
    
    // Page numbers
    for (let i = 1; i <= window.totalPages; i++) {
        pagination.append(`
            <li class="page-item">
                <a class="page-link ${i === window.currentPage ? 'bg-primary-600 text-white' : 'bg-neutral-300 dark:bg-neutral-600 text-secondary-light hover:bg-neutral-400 dark:hover:bg-neutral-500'} font-semibold rounded-lg border-0 flex items-center justify-center h-8 w-8"
                    href="javascript:void(0)" data-page="${i}">${i}</a>
            </li>
        `);
    }
    
    // Next button (only show if not on last page)
    if (window.currentPage < window.totalPages) {
        pagination.append(`
            <li class="page-item">
                <a class="page-link bg-neutral-300 dark:bg-neutral-600 text-secondary-light font-semibold rounded-lg border-0 flex items-center justify-center h-8 w-8 text-base hover:bg-neutral-400 dark:hover:bg-neutral-500"
                    href="javascript:void(0)" data-page="${window.currentPage + 1}">
                    <iconify-icon icon="ep:d-arrow-right"></iconify-icon>
                </a>
            </li>
        `);
    }
}

function updateShowingEntries(data) {
    const perPage = parseInt($('.per-page-select').val());
    const start = ((window.currentPage - 1) * perPage) + 1;
    const end = Math.min(start + perPage - 1, data.total_users);
    const total = data.total_users;
    $('.showing-entries').text(`Showing ${start} to ${end} of ${total} entries`);
}

// ======================== Main Script =====================
$(document).ready(function () {
    const UserListState = {
        currentPage: 1,
        totalPages: 1,
        allUsers: null,
        showOnlyAdmins: false,
        
        refresh(page = this.currentPage) {
            loadUsers(page);
        },
        
        updateFilter() {
            this.filterAndRenderUsers();
        },
        
        filterAndRenderUsers() {
            if (!this.allUsers) return;
            const filteredUsers = filterUsers(this.allUsers);
            const tbody = $('tbody');
            tbody.empty();
            
            if (filteredUsers.length === 0) {
                tbody.append(renderEmptyState());
                $('.showing-entries').text('Showing 0 to 0 of 0 entries');
                return;
            }
            
            // Update the table with filtered users but keep pagination state
            const perPage = parseInt($('.per-page-select').val()) || 10;
            const startIndex = (window.currentPage - 1) * perPage;
            const paginatedUsers = filteredUsers.slice(startIndex, startIndex + perPage);
            
            paginatedUsers.forEach((user, index) => {
                tbody.append(renderUserRow(user, startIndex + index, false));
            });
            
            // Update showing entries with correct pagination info
            const totalUsers = filteredUsers.length;
            const start = Math.min(startIndex + 1, totalUsers);
            const end = Math.min(startIndex + perPage, totalUsers);
            $('.showing-entries').text(`Showing ${start} to ${end} of ${totalUsers} entries`);
        }
    };
    
    window.currentPage = 1;
    window.totalPages = 1;
    window.allUsers = null;
    let showOnlyAdmins = false;
    function loadUsers(page = 1, isFilterChange = false) {
        // Update the current page immediately
        window.currentPage = page;
        
        const search = $('input[name="table-search"]').val();
        const status = $('select:eq(1)').val();
        const perPage = parseInt($('.per-page-select').val());
        const is_staff = showOnlyAdmins ? 'true' : 'all';
        
        // If it's a filter change, reset to first page
        if (isFilterChange) {
            window.currentPage = 1;
            page = 1;
        }
        
        // Show loading state
        const tbody = $('tbody');
        tbody.html('<tr><td colspan="8" class="text-center py-4"><span class="text-base mb-0 font-normal text-secondary-light">Loading...</span></td></tr>');
        
        $.get('/aiwave/admin/api/users/', {
            page: page,
            search: search,
            status: status,
            per_page: perPage,
            is_staff: is_staff
        })
        .done(function (data) {
            tbody.empty();
            if (!data.users || data.users.length === 0) {
                tbody.append(renderEmptyState());
                $('.showing-entries').text('Showing 0 to 0 of 0 entries');
                return;
            }
            window.allUsers = data.users;
            UserListState.allUsers = data.users;
            const filteredUsers = filterUsers(data.users);
            filteredUsers.forEach((user, index) => {
                tbody.append(renderUserRow(user, index, false));
            });
            updatePagination(data);
            updateShowingEntries(data);
        })
        .fail(function(xhr, status, error) {
            tbody.html('<tr><td colspan="8" class="text-center py-4"><span class="text-base mb-0 font-normal text-danger-600">Error loading users. Please try again.</span></td></tr>');
        });
    }
    // Search input handler
    $('input[name="table-search"]').on('input', debounce(function () {
        loadUsers(1, true);
    }, 300));
    
    // Status filter handler
    $('select:eq(1)').on('change', function () {
        // Trigger a new load with filter change flag
        loadUsers(1, true);
    });
    // Pagination click handler
    $('.pagination').on('click', 'a', function (e) {
        e.preventDefault();
        const page = $(this).data('page');
        if (page >= 1 && page <= window.totalPages) {
            loadUsers(page);
        }
    });
    // Per page selection handler
    $('.per-page-select').on('change', function () {
        window.currentPage = 1;
        loadUsers(1);
    });
    // Select all checkbox handler
    $('#selectAll').on('change', function () {
        $('input[name="checkbox"]').prop('checked', $(this).prop('checked'));
    });
    // Status toggle handler
    $(document).on('click', '.toggle-status-btn', function () {
        const button = $(this);
        const userId = button.data('user-id');
        button.prop('disabled', true);
        fetch(`/aiwave/admin/api/users/${userId}/toggle-status/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const newStatus = data.status;
                const newClass = newStatus === 'Active'
                    ? 'bg-success-100 dark:bg-success-600/25 text-success-600 dark:text-success-400 border border-success-600'
                    : 'bg-danger-100 dark:bg-danger-600/25 text-danger-600 dark:text-danger-400 border border-danger-600';
                button.removeClass().addClass(`toggle-status-btn ${newClass} px-4 py-1.5 rounded font-medium text-sm cursor-pointer hover:opacity-80 transition-opacity`);
                button.text(newStatus);
                // Re-apply fixed width and style
                button.css({
                    'min-width': '80px',
                    'white-space': 'nowrap',
                    'display': 'inline-block',
                    'overflow': 'visible'
                });
                // Instead of updating local state, refresh the data from the server
                // This ensures we have the latest data including the correct total count
                loadUsers(window.currentPage);
            }
        })
        .finally(() => button.prop('disabled', false));
    });
    // Delete user handler
    $(document).on('click', '.remove-item-btn', function () {
        const button = $(this);
        const isConfirming = button.data('confirming') === true;
        
        if (!isConfirming) {
            // First click - show confirmation state
            button.data('confirming', true);
            button.html('Confirm');
            button.removeClass('bg-danger-100 dark:bg-danger-600/25 hover:bg-danger-200 text-danger-600 dark:text-danger-500');
            button.addClass('bg-danger-600 hover:bg-danger-700 text-white');
            
            // Reset to original state after 3 seconds
            setTimeout(() => {
                if (button.data('confirming') === true) {
                    button.data('confirming', false);
                    button.html('<iconify-icon icon="fluent:delete-24-regular" class="menu-icon"></iconify-icon>');
                    button.removeClass('bg-danger-600 hover:bg-danger-700 text-white');
                    button.addClass('bg-danger-100 dark:bg-danger-600/25 hover:bg-danger-200 text-danger-600 dark:text-danger-500');
                }
            }, 3000);
        } else {
            // Second click - actually delete
            const userId = button.data('user-id');
            
            button.prop('disabled', true);
            button.html('Deleting...');
            
            fetch(`/aiwave/admin/api/users/${userId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    button.closest('tr').fadeOut(400, function () {
                        $(this).remove();
                        loadUsers(window.currentPage);
                        // User deleted successfully
                    });
                } else {
                    // Reset button state on error
                    button.data('confirming', false);
                    button.prop('disabled', false);
                    button.html('<iconify-icon icon="fluent:delete-24-regular" class="menu-icon"></iconify-icon>');
                    button.removeClass('bg-danger-600 hover:bg-danger-700 text-white');
                    button.addClass('bg-danger-100 dark:bg-danger-600/25 hover:bg-danger-200 text-danger-600 dark:text-danger-500');
                }
            })
            .catch(error => {
                // Reset button state on error
                button.data('confirming', false);
                button.prop('disabled', false);
                button.html('<iconify-icon icon="fluent:delete-24-regular" class="menu-icon"></iconify-icon>');
                button.removeClass('bg-danger-600 hover:bg-danger-700 text-white');
                button.addClass('bg-danger-100 dark:bg-danger-600/25 hover:bg-danger-200 text-danger-600 dark:text-danger-500');
            });
        }
    });
    // Toggle admin button handler
    $('#toggle-admin-btn').on('click', function () {
        showOnlyAdmins = !showOnlyAdmins;
        $(this).text(showOnlyAdmins ? 'Show All Users' : 'Show Only Admins');
        loadUsers(1);
    });
    // ======================== Initialization =====================
    loadUsers();
});