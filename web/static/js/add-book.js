// Add book page functionality
const API_BASE_URL = 'http://localhost:8000/api';

// Preview image when selected
document.addEventListener('DOMContentLoaded', () => {
    const coverImageInput = document.getElementById('cover_image');
    const imagePreview = document.getElementById('image-preview');

    coverImageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            };
            reader.readAsDataURL(file);
        } else {
            imagePreview.innerHTML = '';
        }
    });

    // Handle add book form submission
    const addBookForm = document.getElementById('add-book-form');
    addBookForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleAddBook(e.target);
    });

    // Handle bulk upload form submission
    const bulkUploadForm = document.getElementById('bulk-upload-form');
    bulkUploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleBulkUpload(e.target);
    });
});

async function handleAddBook(form) {
    const formMessage = document.getElementById('form-message');
    formMessage.style.display = 'none';

    const formData = new FormData(form);

    // Remove cover_image if no file is selected
    if (!formData.get('cover_image').name) {
        formData.delete('cover_image');
    }

    // Convert available_quantity to match quantity on creation
    const quantity = formData.get('quantity');
    formData.set('available_quantity', quantity);

    try {
        const response = await apiRequest(`${API_BASE_URL}/books/`, {
            method: 'POST',
            body: formData
        });

        if (!response) {
            // User was redirected to login
            return;
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(JSON.stringify(errorData));
        }

        const book = await response.json();

        // Show success message
        formMessage.className = 'form-message success';
        formMessage.textContent = `Livro "${book.title}" cadastrado com sucesso!`;
        formMessage.style.display = 'block';

        // Reset form
        form.reset();
        document.getElementById('image-preview').innerHTML = '';

        // Redirect to catalog after 2 seconds
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
    } catch (error) {
        console.error('Error adding book:', error);

        formMessage.className = 'form-message error';

        try {
            const errorObj = JSON.parse(error.message);
            const errorMessages = Object.entries(errorObj)
                .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                .join('\n');
            formMessage.textContent = `Erro ao cadastrar livro:\n${errorMessages}`;
        } catch {
            formMessage.textContent = 'Erro ao cadastrar livro. Por favor, verifique os dados e tente novamente.';
        }

        formMessage.style.display = 'block';
    }
}

async function handleBulkUpload(form) {
    const bulkMessage = document.getElementById('bulk-message');
    bulkMessage.style.display = 'none';

    const formData = new FormData(form);

    try {
        const response = await apiRequest(`${API_BASE_URL}/books/bulk_upload/`, {
            method: 'POST',
            body: formData
        });

        if (!response) {
            // User was redirected to login
            return;
        }

        const data = await response.json();

        if (response.ok) {
            bulkMessage.className = 'form-message success';
            bulkMessage.textContent = `${data.message}\nLivros criados: ${data.created}`;

            if (data.errors && data.errors.length > 0) {
                bulkMessage.textContent += `\n\nErros (${data.errors.length}):\n${data.errors.slice(0, 5).join('\n')}`;
                if (data.errors.length > 5) {
                    bulkMessage.textContent += `\n... e mais ${data.errors.length - 5} erros.`;
                }
            }
        } else {
            bulkMessage.className = 'form-message error';
            bulkMessage.textContent = data.message || 'Erro ao importar livros.';

            if (data.errors && data.errors.length > 0) {
                bulkMessage.textContent += `\n\nErros:\n${data.errors.slice(0, 5).join('\n')}`;
                if (data.errors.length > 5) {
                    bulkMessage.textContent += `\n... e mais ${data.errors.length - 5} erros.`;
                }
            }
        }

        bulkMessage.style.display = 'block';

        // Reset form on success
        if (response.ok && data.created > 0) {
            form.reset();

            // Redirect to catalog after 3 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 3000);
        }
    } catch (error) {
        console.error('Error uploading file:', error);

        bulkMessage.className = 'form-message error';
        bulkMessage.textContent = 'Erro ao importar arquivo. Por favor, verifique o formato e tente novamente.';
        bulkMessage.style.display = 'block';
    }
}
