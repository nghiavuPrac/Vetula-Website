// Get all remove icons
const removeIcons = document.querySelectorAll('.remove-icon');

// Add click event listener to each remove icon
removeIcons.forEach(removeIcon => {
    removeIcon.addEventListener('click', () => {
        // Show confirmation prompt
        const confirmed = confirm('Are you sure you want to remove this item?');

        if (confirmed) {
            // Get the item ID from the data attribute
            const itemId = removeIcon.getAttribute('data-item-id');

            // Send AJAX request to the Django endpoint
            fetch(`user/remove-item/${itemId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',  // Include CSRF token if using Django's CSRF protection
                },
            })
                .then(response => {
                    if (response.ok) {
                        // Handle successful removal
                        // const successMessage = response.headers.get('X-Message');
                        // if (successMessage){
                        //     alert(successMessage);
                        // }

                        // Reload the page
                        location.reload();
                    } else {
                        // Handle removal failure
                        console.error('Failed to remove item.');
                    }
                })
                .catch(error => {
                    console.error('An error occurred:', error);
                });
        }
    });
});

                    