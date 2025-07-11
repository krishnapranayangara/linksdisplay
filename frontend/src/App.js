import React, { useState, useEffect } from 'react';
import './App.css';

// Import the new logo
const logoUrl = process.env.PUBLIC_URL + '/linksdisplay-logo.png';

const API_BASE_URL = 'http://localhost:3001/api';

function App() {
  // State
  const [categories, setCategories] = useState([]);
  const [links, setLinks] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showAddLink, setShowAddLink] = useState(false);
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [showEditLink, setShowEditLink] = useState(false);
  const [editingLink, setEditingLink] = useState(null);
  const [newLink, setNewLink] = useState({ title: '', url: '', categoryId: '' });
  const [newCategory, setNewCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // API Functions
  const apiCall = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'API request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  };

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [categoriesResponse, linksResponse] = await Promise.all([
        apiCall('/categories'),
        apiCall('/links')
      ]);
      
      setCategories(categoriesResponse.data || []);
      setLinks(linksResponse.data || []);
      
      // Set default category for new links
      if (categoriesResponse.data && categoriesResponse.data.length > 0) {
        setNewLink(prev => ({ ...prev, categoryId: categoriesResponse.data[0].id }));
      }
    } catch (error) {
      setError('Failed to load data: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Handlers
  const handleAddLink = async () => {
    if (!newLink.title || !newLink.url) return;
    
    try {
      // Set category to currently selected category if not "All"
      const categoryId = selectedCategory === 'All' ? newLink.categoryId : selectedCategory;
      
      const newLinkData = await apiCall('/links', {
        method: 'POST',
        body: JSON.stringify({
          title: newLink.title,
          url: newLink.url,
          categoryId: categoryId || null,
          pinned: false,
        }),
      });
      
      setLinks(prev => [...prev, newLinkData.data || newLinkData]);
      setShowAddLink(false);
      setNewLink({ title: '', url: '', categoryId: categories[0]?.id || '' });
    } catch (error) {
      setError('Failed to add link: ' + error.message);
    }
  };

  const handleEditLink = async () => {
    if (!editingLink.title || !editingLink.url) return;
    
    try {
      const updatedLink = await apiCall(`/links/${editingLink.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          title: editingLink.title,
          url: editingLink.url,
          categoryId: editingLink.categoryId || null,
          pinned: editingLink.pinned,
        }),
      });
      
      setLinks(prev => prev.map(l => l.id === editingLink.id ? (updatedLink.data || updatedLink) : l));
      setShowEditLink(false);
      setEditingLink(null);
    } catch (error) {
      setError('Failed to update link: ' + error.message);
    }
  };

  const handleStartEdit = (link) => {
    setEditingLink({ ...link });
    setShowEditLink(true);
  };

  const handleDeleteLink = async (id) => {
    try {
      await apiCall(`/links/${id}`, { method: 'DELETE' });
      setLinks(prev => prev.filter(l => l.id !== id));
    } catch (error) {
      setError('Failed to delete link: ' + error.message);
    }
  };

  const handlePinLink = async (id) => {
    try {
      const link = links.find(l => l.id === id);
      const newPinnedStatus = !link.pinned;
      
      await apiCall(`/links/${id}/pin`, {
        method: 'PATCH',
        body: JSON.stringify({ pinned: newPinnedStatus }),
      });
      
      setLinks(prev => prev.map(l => l.id === id ? { ...l, pinned: newPinnedStatus } : l));
    } catch (error) {
      setError('Failed to update pin status: ' + error.message);
    }
  };

  const handleAddCategory = async () => {
    if (!newCategory.trim()) return;
    
    try {
      const newCategoryData = await apiCall('/categories', {
        method: 'POST',
        body: JSON.stringify({ name: newCategory.trim() }),
      });
      
      setCategories(prev => [...prev, newCategoryData.data || newCategoryData]);
      setShowAddCategory(false);
      setNewCategory('');
      
      // Update newLink categoryId if it was empty
      if (!newLink.categoryId) {
        setNewLink(prev => ({ ...prev, categoryId: (newCategoryData.data || newCategoryData).id }));
      }
    } catch (error) {
      setError('Failed to add category: ' + error.message);
    }
  };

  const handleDeleteCategory = async (id) => {
    try {
      await apiCall(`/categories/${id}`, { method: 'DELETE' });
      setCategories(prev => prev.filter(c => c.id !== id));
      setLinks(prev => prev.map(l => l.categoryId === id ? { ...l, categoryId: null } : l));
    } catch (error) {
      setError('Failed to delete category: ' + error.message);
    }
  };

  // Filtered and sorted links
  const filteredLinks =
    selectedCategory === 'All'
      ? links
      : links.filter((l) => l.categoryId === selectedCategory);
  const sortedLinks = [
    ...filteredLinks.filter((l) => l.pinned),
    ...filteredLinks.filter((l) => !l.pinned),
  ];

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  // Responsive UI
  return (
    <div className="app-container">
      <header>
        <img src={logoUrl} alt="linksdisplay logo" style={{ width: 120, margin: '24px auto 8px', display: 'block' }} />
        {/* <h1>🔗 Link Organizer</h1> */}
        <p>Your links, organized.</p>
        <div style={{ fontSize: '0.9em', color: '#888', marginTop: 4 }}>a product of perspective computing</div>
      </header>
      
      {error && (
        <div className="error-message" onClick={() => setError('')}>
          ❌ {error} (click to dismiss)
        </div>
      )}
      
      <div className="category-bar">
        <button
          className={selectedCategory === 'All' ? 'active' : ''}
          onClick={() => setSelectedCategory('All')}
        >
          All
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            className={selectedCategory === cat.id ? 'active' : ''}
            onClick={() => setSelectedCategory(cat.id)}
          >
            {cat.name}
            <span
              className="delete-category"
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteCategory(cat.id);
              }}
              title="Delete category"
            >
              ×
            </span>
          </button>
        ))}
        <button className="add-btn" onClick={() => setShowAddCategory(true)}>
          ＋
        </button>
      </div>
      <div className="actions">
        <button className="add-btn" onClick={() => setShowAddLink(true)}>
          Add Link
        </button>
      </div>
      <main>
        {sortedLinks.length === 0 ? (
          <div className="empty">No links yet. Add your first link!</div>
        ) : (
          <ul className="link-list">
            {sortedLinks.map((link) => (
              <li key={link.id} className={link.pinned ? 'pinned' : ''}>
                <div className="link-main">
                  <a href={link.url} target="_blank" rel="noopener noreferrer">
                    {link.title}
                  </a>
                  <span className="category-label">
                    {categories.find((c) => c.id === link.categoryId)?.name || 'Uncategorized'}
                  </span>
                </div>
                <div className="link-actions">
                  <button onClick={() => handleStartEdit(link)} title="Edit">
                    ✏️
                  </button>
                  <button onClick={() => handlePinLink(link.id)} title={link.pinned ? 'Unpin' : 'Pin'}>
                    {link.pinned ? '📌' : '📍'}
                  </button>
                  <button onClick={() => handleDeleteLink(link.id)} title="Delete">
                    🗑️
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>
      {/* Add Link Modal */}
      {showAddLink && (
        <div className="modal-overlay" onClick={() => setShowAddLink(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Add Link</h2>
            <input
              type="text"
              placeholder="Title"
              value={newLink.title}
              onChange={(e) => setNewLink({ ...newLink, title: e.target.value })}
            />
            <input
              type="url"
              placeholder="URL"
              value={newLink.url}
              onChange={(e) => setNewLink({ ...newLink, url: e.target.value })}
            />
            <select
              value={selectedCategory === 'All' ? newLink.categoryId : selectedCategory}
              onChange={(e) => setNewLink({ ...newLink, categoryId: Number(e.target.value) || null })}
            >
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
            <div className="modal-actions">
              <button onClick={() => setShowAddLink(false)}>Cancel</button>
              <button onClick={handleAddLink}>Add</button>
            </div>
          </div>
        </div>
      )}
      {/* Edit Link Modal */}
      {showEditLink && editingLink && (
        <div className="modal-overlay" onClick={() => setShowEditLink(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Edit Link</h2>
            <input
              type="text"
              placeholder="Title"
              value={editingLink.title}
              onChange={(e) => setEditingLink({ ...editingLink, title: e.target.value })}
            />
            <input
              type="url"
              placeholder="URL"
              value={editingLink.url}
              onChange={(e) => setEditingLink({ ...editingLink, url: e.target.value })}
            />
            <select
              value={editingLink.categoryId || ''}
              onChange={(e) => setEditingLink({ ...editingLink, categoryId: Number(e.target.value) || null })}
            >
              <option value="">Uncategorized</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
            <div className="modal-actions">
              <button onClick={() => setShowEditLink(false)}>Cancel</button>
              <button onClick={handleEditLink}>Save</button>
            </div>
          </div>
        </div>
      )}
      {/* Add Category Modal */}
      {showAddCategory && (
        <div className="modal-overlay" onClick={() => setShowAddCategory(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Add Category</h2>
            <input
              type="text"
              placeholder="Category name"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
            />
            <div className="modal-actions">
              <button onClick={() => setShowAddCategory(false)}>Cancel</button>
              <button onClick={handleAddCategory}>Add</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
