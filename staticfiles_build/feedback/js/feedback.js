const feedbackForm = document.getElementById('feedbackForm');

if (feedbackForm) {
    feedbackForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const rating = document.querySelector('input[name="rating"]:checked');
        
        const formData = {
            name: document.getElementById('feedback-name').value || 'Anonymous',
            email: document.getElementById('feedback-email').value || 'Not provided',
            type: document.getElementById('feedback-type').value,
            rating: rating ? rating.value : 'Not rated',
            message: document.getElementById('feedback-message').value
        };
        
        console.log('Feedback Submitted:', formData);

        alert('Thank you for your feedback! Your input helps us improve.');

        feedbackForm.reset();
})
};