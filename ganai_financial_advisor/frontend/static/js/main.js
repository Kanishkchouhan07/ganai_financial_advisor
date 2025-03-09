// Global variables
let currentCategory = document.querySelector('.category-button[data-category]')?.dataset.category || 'general';

// Function to select a category
function selectCategory(categoryId) {
    currentCategory = categoryId;
    
    // Update button styles
    document.querySelectorAll('.category-button').forEach(button => {
        if (button.dataset.category === categoryId) {
            button.classList.remove('btn-outline-primary');
            button.classList.add('btn-primary');
        } else {
            button.classList.remove('btn-primary');
            button.classList.add('btn-outline-primary');
        }
    });
    
    // Update category name in the query section
    const categoryName = document.querySelector(`.category-button[data-category="${categoryId}"]`).textContent;
    document.getElementById('selectedCategoryName').textContent = categoryName;
    
    // Update query input placeholder
    document.getElementById('queryInput').placeholder = `Example: What are some good strategies for ${categoryId} investing?`;
}

// Function to submit a query
async function submitQuery(event) {
    event.preventDefault();
    
    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();
    
    if (!query) return;
    
    // Show loading state
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
    submitButton.disabled = true;
    
    try {
        const response = await fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                query: query,
                category: currentCategory
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show response area
            const responseArea = document.getElementById('responseArea');
            responseArea.style.display = 'block';
            responseArea.classList.add('fade-in');
            
            // Update response text
            document.getElementById('responseText').innerHTML = data.response;
            
            // Handle visualization if available
            const visualizationArea = document.getElementById('visualizationArea');
            const plotArea = document.getElementById('plotArea');
            
            if (data.graphJSON) {
                visualizationArea.style.display = 'block';
                Plotly.newPlot('plotArea', JSON.parse(data.graphJSON));
            } else {
                visualizationArea.style.display = 'none';
            }
            
            // Clear input
            queryInput.value = '';
            
            // Scroll to response
            responseArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            showError('Failed to get response from the server');
        }
    } catch (error) {
        showError('An error occurred while processing your request');
        console.error('Error:', error);
    } finally {
        // Reset button state
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
    }
}

// Function to load a history item
function loadHistoryItem(query, category) {
    // Select the category
    selectCategory(category);
    
    // Set the query
    const queryInput = document.getElementById('queryInput');
    queryInput.value = query;
    
    // Submit the form
    document.getElementById('queryForm').dispatchEvent(new Event('submit'));
}

// Function to use a sample question
function useQuestion(question) {
    document.getElementById('queryInput').value = question;
}

// Function to clear history
async function clearHistory() {
    try {
        const response = await fetch('/clear-history', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Reload the page to reflect the cleared history
            window.location.reload();
        } else {
            showError('Failed to clear history');
        }
    } catch (error) {
        showError('An error occurred while clearing history');
        console.error('Error:', error);
    }
}

// Function to show error messages
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.querySelector('.content-wrapper').insertBefore(
        errorDiv,
        document.querySelector('.category-section')
    );
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize form submission
    const queryForm = document.getElementById('queryForm');
    if (queryForm) {
        queryForm.addEventListener('submit', submitQuery);
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 