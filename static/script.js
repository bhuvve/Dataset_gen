document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('datasetForm');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const downloadLink = document.getElementById('downloadLink');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show loading state
        loading.classList.remove('hidden');
        result.classList.add('hidden');

        const formData = {
            num_rows: parseInt(document.getElementById('numRows').value),
            prompt: document.getElementById('prompt').value,
            backstory: document.getElementById('backstory').value || null
        };

        try {
            const response = await fetch('/generate-dataset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                // Show success message and download link
                result.classList.remove('hidden');
                downloadLink.href = data.download_url;
                
                // Add success animation
                result.classList.add('animate__animated', 'animate__fadeIn');
            } else {
                throw new Error(data.detail || 'Failed to generate dataset');
            }
        } catch (error) {
            // Show error message
            alert('Error: ' + error.message);
        } finally {
            // Hide loading state
            loading.classList.add('hidden');
        }
    });

    // Add input validation
    const numRowsInput = document.getElementById('numRows');
    numRowsInput.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        if (value < 1) e.target.value = 1;
        if (value > 1000) e.target.value = 1000;
    });

    // Add animation to form elements
    const formElements = form.querySelectorAll('input, textarea, button');
    formElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });
}); 