/**
 * Lightning Digital Marketplace - Store JavaScript
 * Stage 2: Commerce Core
 * 
 * Handles product listing, search, and store functionality
 */

class LightningStore {
    constructor() {
        this.products = [];
        this.filteredProducts = [];
        this.categories = [];
        this.currentFilter = 'all';
        this.currentSearch = '';
        this.sortBy = 'name';
        this.sortOrder = 'asc';
        
        this.init();
    }
    
    init() {
        this.loadProducts();
        this.loadCategories();
        this.setupEventListeners();
    }
    
    async loadProducts() {
        try {
            this.showLoadingState();
            
            const response = await fetch('/api/products');
            const data = await response.json();
            
            if (data.success) {
                this.products = data.products;
                this.filteredProducts = [...this.products];
                this.displayProducts();
                this.updateProductCount();
            } else {
                throw new Error(data.error || 'Failed to load products');
            }
        } catch (error) {
            this.showError('Failed to load products: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }
    
    async loadCategories() {
        try {
            const response = await fetch('/api/categories');
            const data = await response.json();
            
            if (data.success) {
                this.categories = data.categories;
                this.displayCategories();
            }
        } catch (error) {
            console.error('Failed to load categories:', error);
        }
    }
    
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('productSearch');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(() => {
                this.currentSearch = searchInput.value.trim();
                this.filterProducts();
            }, 300));
        }
        
        // Category filter
        const categorySelect = document.getElementById('categoryFilter');
        if (categorySelect) {
            categorySelect.addEventListener('change', () => {
                this.currentFilter = categorySelect.value;
                this.filterProducts();
            });
        }
        
        // Sort functionality
        const sortSelect = document.getElementById('sortProducts');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => {
                const [sortBy, sortOrder] = sortSelect.value.split('_');
                this.sortBy = sortBy;
                this.sortOrder = sortOrder;
                this.sortProducts();
                this.displayProducts();
            });
        }
        
        // Clear filters button
        const clearFiltersButton = document.getElementById('clearFilters');
        if (clearFiltersButton) {
            clearFiltersButton.addEventListener('click', () => {
                this.clearFilters();
            });
        }
    }
    
    displayProducts() {
        const container = document.getElementById('productsContainer');
        if (!container) return;
        
        if (this.filteredProducts.length === 0) {
            this.showNoProducts();
            return;
        }
        
        const html = this.filteredProducts.map(product => this.createProductCard(product)).join('');
        container.innerHTML = html;
        
        // Setup buy now buttons
        this.setupBuyNowButtons();
    }
    
    createProductCard(product) {
        const imageUrl = product.image_url || '/static/images/product-placeholder.png';
        const isAvailable = product.is_available !== false;
        
        return `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100 product-card ${!isAvailable ? 'product-unavailable' : ''}" data-product-id="${product.id}">
                    <div class="position-relative">
                        <img src="${imageUrl}" class="card-img-top" alt="${product.name}" style="height: 200px; object-fit: cover;">
                        ${!isAvailable ? '<div class="position-absolute top-0 end-0 m-2 badge bg-secondary">Out of Stock</div>' : ''}
                        ${product.featured ? '<div class="position-absolute top-0 start-0 m-2 badge bg-warning text-dark">Featured</div>' : ''}
                    </div>
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text text-muted flex-grow-1">${product.description}</p>
                        
                        <div class="product-meta mb-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="price">
                                    <span class="h5 text-success mb-0">${product.price_sats.toLocaleString()} sats</span>
                                    <br>
                                    <small class="text-muted">${product.price_btc.toFixed(8)} BTC</small>
                                </div>
                                <div class="category">
                                    <span class="badge bg-primary">${product.category}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="product-actions">
                            ${isAvailable ? `
                                <button class="btn btn-success w-100 buy-now-btn" data-product-id="${product.id}">
                                    <i class="fas fa-bolt"></i> Buy with Lightning
                                </button>
                            ` : `
                                <button class="btn btn-secondary w-100" disabled>
                                    <i class="fas fa-times"></i> Unavailable
                                </button>
                            `}
                            <div class="mt-2 d-flex justify-content-between">
                                <button class="btn btn-outline-info btn-sm view-details-btn" data-product-id="${product.id}">
                                    <i class="fas fa-info-circle"></i> Details
                                </button>
                                <button class="btn btn-outline-secondary btn-sm share-btn" data-product-id="${product.id}">
                                    <i class="fas fa-share"></i> Share
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    ${product.tags && product.tags.length > 0 ? `
                        <div class="card-footer">
                            <small class="text-muted">
                                ${product.tags.map(tag => `<span class="badge bg-light text-dark me-1">${tag}</span>`).join('')}
                            </small>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    displayCategories() {
        const categorySelect = document.getElementById('categoryFilter');
        if (!categorySelect) return;
        
        let options = '<option value="all">All Categories</option>';
        this.categories.forEach(category => {
            options += `<option value="${category}">${category}</option>`;
        });
        
        categorySelect.innerHTML = options;
    }
    
    filterProducts() {
        this.filteredProducts = this.products.filter(product => {
            // Category filter
            const matchesCategory = this.currentFilter === 'all' || product.category === this.currentFilter;
            
            // Search filter
            const matchesSearch = !this.currentSearch || 
                product.name.toLowerCase().includes(this.currentSearch.toLowerCase()) ||
                product.description.toLowerCase().includes(this.currentSearch.toLowerCase()) ||
                (product.tags && product.tags.some(tag => tag.toLowerCase().includes(this.currentSearch.toLowerCase())));
            
            return matchesCategory && matchesSearch;
        });
        
        this.sortProducts();
        this.displayProducts();
        this.updateProductCount();
        this.updateClearFiltersButton();
    }
    
    sortProducts() {
        this.filteredProducts.sort((a, b) => {
            let valueA, valueB;
            
            switch (this.sortBy) {
                case 'name':
                    valueA = a.name.toLowerCase();
                    valueB = b.name.toLowerCase();
                    break;
                case 'price':
                    valueA = a.price_sats;
                    valueB = b.price_sats;
                    break;
                case 'category':
                    valueA = a.category.toLowerCase();
                    valueB = b.category.toLowerCase();
                    break;
                default:
                    valueA = a.name.toLowerCase();
                    valueB = b.name.toLowerCase();
            }
            
            if (typeof valueA === 'string') {
                return this.sortOrder === 'asc' ? 
                    valueA.localeCompare(valueB) : 
                    valueB.localeCompare(valueA);
            } else {
                return this.sortOrder === 'asc' ? 
                    valueA - valueB : 
                    valueB - valueA;
            }
        });
    }
    
    setupBuyNowButtons() {
        const buyButtons = document.querySelectorAll('.buy-now-btn');
        buyButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = e.target.closest('.buy-now-btn').dataset.productId;
                this.redirectToCheckout(productId);
            });
        });
        
        const detailButtons = document.querySelectorAll('.view-details-btn');
        detailButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = e.target.closest('.view-details-btn').dataset.productId;
                this.showProductDetails(productId);
            });
        });
        
        const shareButtons = document.querySelectorAll('.share-btn');
        shareButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = e.target.closest('.share-btn').dataset.productId;
                this.shareProduct(productId);
            });
        });
    }
    
    redirectToCheckout(productId) {
        window.location.href = `/checkout/${productId}`;
    }
    
    showProductDetails(productId) {
        const product = this.products.find(p => p.id == productId);
        if (!product) return;
        
        // Create and show modal with product details
        const modalHtml = `
            <div class="modal fade" id="productDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${product.name}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <img src="${product.image_url || '/static/images/product-placeholder.png'}" 
                                         class="img-fluid rounded" alt="${product.name}">
                                </div>
                                <div class="col-md-6">
                                    <h6>Description</h6>
                                    <p>${product.description}</p>
                                    
                                    <h6>Price</h6>
                                    <p class="text-success h5">${product.price_sats.toLocaleString()} sats</p>
                                    <p class="text-muted">${product.price_btc.toFixed(8)} BTC</p>
                                    
                                    <h6>Category</h6>
                                    <p><span class="badge bg-primary">${product.category}</span></p>
                                    
                                    ${product.tags && product.tags.length > 0 ? `
                                        <h6>Tags</h6>
                                        <p>${product.tags.map(tag => `<span class="badge bg-light text-dark me-1">${tag}</span>`).join('')}</p>
                                    ` : ''}
                                    
                                    ${product.file_size ? `
                                        <h6>File Size</h6>
                                        <p>${product.file_size}</p>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            ${product.is_available !== false ? `
                                <button type="button" class="btn btn-success" onclick="window.location.href='/checkout/${product.id}'">
                                    <i class="fas fa-bolt"></i> Buy with Lightning
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal
        const existingModal = document.getElementById('productDetailsModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('productDetailsModal'));
        modal.show();
    }
    
    async shareProduct(productId) {
        const product = this.products.find(p => p.id == productId);
        if (!product) return;
        
        const shareData = {
            title: `${product.name} - Lightning Marketplace`,
            text: product.description,
            url: `${window.location.origin}/checkout/${product.id}`
        };
        
        try {
            // Use Web Share API if available
            if (navigator.share) {
                await navigator.share(shareData);
            } else {
                // Fallback: copy to clipboard
                await navigator.clipboard.writeText(shareData.url);
                this.showSuccess('Product link copied to clipboard!');
            }
        } catch (error) {
            // Final fallback: show share modal
            this.showShareModal(product, shareData.url);
        }
    }
    
    showShareModal(product, url) {
        const modalHtml = `
            <div class="modal fade" id="shareModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-share"></i> Share ${product.name}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Product URL:</label>
                                <div class="input-group">
                                    <input type="text" class="form-control" id="shareUrl" value="${url}" readonly>
                                    <button class="btn btn-outline-primary" onclick="navigator.clipboard.writeText('${url}').then(() => { this.textContent = 'Copied!'; setTimeout(() => this.textContent = 'Copy', 2000); })">
                                        Copy
                                    </button>
                                </div>
                            </div>
                            <div class="d-grid gap-2">
                                <a href="https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(`Check out ${product.name} on Lightning Marketplace!`)}" 
                                   target="_blank" class="btn btn-outline-primary">
                                    <i class="fab fa-twitter"></i> Share on Twitter
                                </a>
                                <a href="mailto:?subject=${encodeURIComponent(product.name)}&body=${encodeURIComponent(`Check out ${product.name}: ${url}`)}" 
                                   class="btn btn-outline-primary">
                                    <i class="fas fa-envelope"></i> Share via Email
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal
        const existingModal = document.getElementById('shareModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('shareModal'));
        modal.show();
    }
    
    clearFilters() {
        this.currentFilter = 'all';
        this.currentSearch = '';
        
        // Reset UI elements
        const searchInput = document.getElementById('productSearch');
        const categorySelect = document.getElementById('categoryFilter');
        const sortSelect = document.getElementById('sortProducts');
        
        if (searchInput) searchInput.value = '';
        if (categorySelect) categorySelect.value = 'all';
        if (sortSelect) sortSelect.value = 'name_asc';
        
        // Reset sort
        this.sortBy = 'name';
        this.sortOrder = 'asc';
        
        // Refilter and display
        this.filterProducts();
    }
    
    updateProductCount() {
        const countElement = document.getElementById('productCount');
        if (countElement) {
            const total = this.products.length;
            const filtered = this.filteredProducts.length;
            
            if (filtered === total) {
                countElement.textContent = `${total} products`;
            } else {
                countElement.textContent = `${filtered} of ${total} products`;
            }
        }
    }
    
    updateClearFiltersButton() {
        const clearButton = document.getElementById('clearFilters');
        if (clearButton) {
            const hasFilters = this.currentFilter !== 'all' || this.currentSearch !== '';
            clearButton.style.display = hasFilters ? 'inline-block' : 'none';
        }
    }
    
    showLoadingState() {
        const container = document.getElementById('productsContainer');
        if (container) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3">Loading products...</p>
                </div>
            `;
        }
    }
    
    hideLoadingState() {
        // Loading state is automatically hidden when displayProducts() is called
    }
    
    showNoProducts() {
        const container = document.getElementById('productsContainer');
        if (container) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5>No products found</h5>
                    <p class="text-muted">
                        ${this.currentSearch || this.currentFilter !== 'all' ? 
                            'Try adjusting your search or filters' : 
                            'No products are currently available'}
                    </p>
                    ${this.currentSearch || this.currentFilter !== 'all' ? 
                        '<button class="btn btn-primary" onclick="lightningStore.clearFilters()">Clear Filters</button>' : ''}
                </div>
            `;
        }
    }
    
    showError(message) {
        const container = document.getElementById('productsContainer');
        if (container) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Error:</strong> ${message}
                    </div>
                </div>
            `;
        }
    }
    
    showSuccess(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0 position-fixed top-0 end-0 m-3';
        toast.style.zIndex = '1070';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 3000);
    }
}

// Utility function for debouncing search input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize store when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const lightningStore = new LightningStore();
    
    // Make it globally accessible for debugging
    window.lightningStore = lightningStore;
    
    console.log('Lightning Store initialized');
});