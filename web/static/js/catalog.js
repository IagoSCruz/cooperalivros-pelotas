// Catalog page functionality
const API_BASE_URL = 'http://localhost:8000/api';

let allBooks = [];
let currentFilter = 'all';

async function loadBooks(filter = 'all') {
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const booksGrid = document.getElementById('books-grid');

    loading.style.display = 'block';
    errorMessage.style.display = 'none';
    booksGrid.innerHTML = '';

    try {
        let url = `${API_BASE_URL}/books/`;
        if (filter === 'available') {
            url = `${API_BASE_URL}/books/available/`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error('Failed to load books');
        }

        const data = await response.json();
        allBooks = data.results || data;

        displayBooks(allBooks);
    } catch (error) {
        console.error('Error loading books:', error);
        errorMessage.textContent = 'Erro ao carregar livros. Por favor, tente novamente.';
        errorMessage.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
}

function displayBooks(books) {
    const booksGrid = document.getElementById('books-grid');
    booksGrid.innerHTML = '';

    if (books.length === 0) {
        booksGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--secondary-color);">Nenhum livro encontrado.</p>';
        return;
    }

    books.forEach(book => {
        const bookCard = createBookCard(book);
        booksGrid.appendChild(bookCard);
    });
}

function createBookCard(book) {
    const card = document.createElement('div');
    card.className = 'book-card';
    card.onclick = () => showBookDetails(book.id);

    const coverDiv = document.createElement('div');
    coverDiv.className = 'book-cover';

    if (book.cover_image) {
        const img = document.createElement('img');
        img.src = book.cover_image;
        img.alt = book.title;
        coverDiv.appendChild(img);
    } else {
        coverDiv.textContent = '📚';
    }

    const infoDiv = document.createElement('div');
    infoDiv.className = 'book-info';

    const title = document.createElement('h3');
    title.className = 'book-title';
    title.textContent = book.title;

    const author = document.createElement('p');
    author.className = 'book-author';
    author.textContent = book.author;

    const meta = document.createElement('div');
    meta.className = 'book-meta';

    if (book.category) {
        const category = document.createElement('span');
        category.className = 'book-category';
        category.textContent = book.category;
        meta.appendChild(category);
    }

    const availability = document.createElement('span');
    availability.className = `book-availability ${book.is_available ? 'available' : 'unavailable'}`;
    availability.textContent = book.is_available ? 'Disponível' : 'Indisponível';
    meta.appendChild(availability);

    infoDiv.appendChild(title);
    infoDiv.appendChild(author);
    infoDiv.appendChild(meta);

    card.appendChild(coverDiv);
    card.appendChild(infoDiv);

    return card;
}

async function showBookDetails(bookId) {
    try {
        const response = await fetch(`${API_BASE_URL}/books/${bookId}/`);

        if (!response.ok) {
            throw new Error('Failed to load book details');
        }

        const book = await response.json();
        displayBookModal(book);
    } catch (error) {
        console.error('Error loading book details:', error);
        alert('Erro ao carregar detalhes do livro.');
    }
}

function displayBookModal(book) {
    const modal = document.getElementById('book-modal');
    const bookDetails = document.getElementById('book-details');

    bookDetails.innerHTML = `
        <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
            <div style="flex: 0 0 200px;">
                ${book.cover_image
                    ? `<img src="${book.cover_image}" alt="${book.title}" style="width: 100%; border-radius: 0.5rem;">`
                    : '<div class="book-cover" style="width: 200px; height: 300px; border-radius: 0.5rem;">📚</div>'
                }
            </div>
            <div style="flex: 1; min-width: 250px;">
                <h2 style="margin-bottom: 1rem;">${book.title}</h2>
                <p style="margin-bottom: 0.5rem;"><strong>Autor:</strong> ${book.author}</p>
                <p style="margin-bottom: 0.5rem;"><strong>ISBN:</strong> ${book.isbn}</p>
                ${book.publisher ? `<p style="margin-bottom: 0.5rem;"><strong>Editora:</strong> ${book.publisher}</p>` : ''}
                ${book.publication_year ? `<p style="margin-bottom: 0.5rem;"><strong>Ano:</strong> ${book.publication_year}</p>` : ''}
                ${book.category ? `<p style="margin-bottom: 0.5rem;"><strong>Categoria:</strong> ${book.category}</p>` : ''}
                <p style="margin-bottom: 0.5rem;"><strong>Quantidade Total:</strong> ${book.quantity}</p>
                <p style="margin-bottom: 0.5rem;"><strong>Disponíveis:</strong> ${book.available_quantity}</p>
                <p style="margin-top: 1rem;">
                    <span class="book-availability ${book.available_quantity > 0 ? 'available' : 'unavailable'}" style="font-size: 1.125rem;">
                        ${book.available_quantity > 0 ? '✓ Disponível para empréstimo' : '✗ Indisponível'}
                    </span>
                </p>
            </div>
        </div>
    `;

    modal.style.display = 'block';
}

function searchBooks(query) {
    if (!query) {
        displayBooks(allBooks);
        return;
    }

    const lowerQuery = query.toLowerCase();
    const filtered = allBooks.filter(book =>
        book.title.toLowerCase().includes(lowerQuery) ||
        book.author.toLowerCase().includes(lowerQuery) ||
        book.isbn.includes(query)
    );

    displayBooks(filtered);
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadBooks();

    // Search functionality
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('search-input');

    searchBtn.addEventListener('click', () => {
        searchBooks(searchInput.value);
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchBooks(searchInput.value);
        }
    });

    // Filter buttons
    const showAllBtn = document.getElementById('show-all');
    const showAvailableBtn = document.getElementById('show-available');

    showAllBtn.addEventListener('click', () => {
        currentFilter = 'all';
        loadBooks('all');
        showAllBtn.classList.add('btn-primary');
        showAllBtn.classList.remove('btn-secondary');
        showAvailableBtn.classList.add('btn-secondary');
        showAvailableBtn.classList.remove('btn-primary');
    });

    showAvailableBtn.addEventListener('click', () => {
        currentFilter = 'available';
        loadBooks('available');
        showAvailableBtn.classList.add('btn-primary');
        showAvailableBtn.classList.remove('btn-secondary');
        showAllBtn.classList.add('btn-secondary');
        showAllBtn.classList.remove('btn-primary');
    });

    // Modal close
    const modal = document.getElementById('book-modal');
    const closeBtn = document.querySelector('.close');

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});
