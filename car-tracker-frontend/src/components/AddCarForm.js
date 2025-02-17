// src/components/AddCarForm.js
import React, { useState } from 'react';

function AddCarForm({ onAdd }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onAdd(url);
      setUrl('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="add-car-form">
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter Facebook Marketplace URL"
      />
      <button type="submit">Add Car</button>
    </form>
  );
}

export default AddCarForm;