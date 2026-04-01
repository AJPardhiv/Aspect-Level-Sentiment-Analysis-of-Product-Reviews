import React, { useState } from 'react';

const EventForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    name: '',
    guest_count: '',
    menu_type: 'veg',
    event_date: '',
    location: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.guest_count || !formData.event_date || !formData.location) {
      alert('Please fill in all fields');
      return;
    }

    onSubmit(formData);
  };

  return (
    <div style={styles.formContainer}>
      <h2 style={styles.heading}>Workflow Request</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.formGroup}>
          <label style={styles.label}>Workflow Name</label>
          <input
            type="text"
            name="name"
            placeholder="e.g., Weekly Lead Qualification"
            value={formData.name}
            onChange={handleChange}
            style={styles.input}
            disabled={isLoading}
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Workload Units</label>
          <input
            type="number"
            name="guest_count"
            placeholder="e.g., 120"
            value={formData.guest_count}
            onChange={handleChange}
            style={styles.input}
            disabled={isLoading}
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Execution Mode</label>
          <select
            name="menu_type"
            value={formData.menu_type}
            onChange={handleChange}
            style={styles.input}
            disabled={isLoading}
          >
            <option value="veg">Sequential</option>
            <option value="non-veg">Parallel</option>
          </select>
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Deadline</label>
          <input
            type="datetime-local"
            name="event_date"
            value={formData.event_date}
            onChange={handleChange}
            style={styles.input}
            disabled={isLoading}
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Target System</label>
          <input
            type="text"
            name="location"
            placeholder="e.g., CRM + Email + Billing"
            value={formData.location}
            onChange={handleChange}
            style={styles.input}
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          style={{
            ...styles.button,
            opacity: isLoading ? 0.7 : 1,
            cursor: isLoading ? 'not-allowed' : 'pointer',
          }}
          disabled={isLoading}
        >
          {isLoading ? '⏳ Running AI...' : '🚀 Run AI'}
        </button>
      </form>
    </div>
  );
};

const styles = {
  formContainer: {
    backgroundColor: '#f5f5f5',
    padding: '30px',
    borderRadius: '8px',
    border: '1px solid #e0e0e0',
    width: '100%',
    maxWidth: '500px',
  },
  heading: {
    fontSize: '20px',
    fontWeight: '600',
    marginBottom: '20px',
    color: '#1a1a1a',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  label: {
    fontSize: '13px',
    fontWeight: '500',
    color: '#333',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  input: {
    padding: '10px 12px',
    fontSize: '14px',
    border: '1px solid #d0d0d0',
    borderRadius: '4px',
    fontFamily: 'inherit',
    backgroundColor: '#fff',
    color: '#1a1a1a',
    transition: 'border-color 0.2s',
  },
  button: {
    padding: '12px 20px',
    fontSize: '16px',
    fontWeight: '600',
    backgroundColor: '#0066cc',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    marginTop: '10px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
};

export default EventForm;
