import { useEffect, useState } from 'react';
import api from '../api/client';
import '../styles/RecurringServices.css';

const defaultFormState = () => ({
  serviceId: '',
  recurrenceType: 'weekly',
  startDateTime: new Date().toISOString().slice(0, 16),
  notes: 'Recurring service',
});

export default function RecurringServices() {
  const [recurringServices, setRecurringServices] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [availableServices, setAvailableServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [servicesLoading, setServicesLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [form, setForm] = useState(defaultFormState);

  useEffect(() => {
    fetchRecurringServices();
    fetchUpcomingReminders();
    fetchAvailableServices();
  }, []);

  useEffect(() => {
    if (!form.serviceId && availableServices.length > 0) {
      setForm((prev) => ({ ...prev, serviceId: String(availableServices[0].id) }));
    }
  }, [availableServices, form.serviceId]);

  const fetchRecurringServices = async () => {
    try {
      const response = await api.get('/recurring-services');
      setRecurringServices(response.data || []);
    } catch (error) {
      console.error('Error fetching recurring services:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUpcomingReminders = async () => {
    try {
      const response = await api.get('/recurring-services/reminders/all');
      setReminders(response.data || []);
    } catch (error) {
      console.error('Error fetching reminders:', error);
    }
  };

  const fetchAvailableServices = async () => {
    setServicesLoading(true);
    try {
      const response = await api.get('/services', { params: { limit: 100 } });
      setAvailableServices(response.data || []);
    } catch (error) {
      console.error('Error fetching services:', error);
    } finally {
      setServicesLoading(false);
    }
  };

  const handleCreateRecurring = async () => {
    if (!form.serviceId) {
      alert('Please select a service first.');
      return;
    }

    const startDate = new Date(form.startDateTime);
    if (Number.isNaN(startDate.getTime())) {
      alert('Please choose a valid start date and time.');
      return;
    }

    setIsCreating(true);
    try {
      const response = await api.post('/recurring-services', {
        service_id: Number(form.serviceId),
        recurrence_type: form.recurrenceType,
        start_date: startDate.toISOString(),
        notes: form.notes || null,
      });

      setRecurringServices((prev) => [...prev, response.data]);
      fetchUpcomingReminders();
      setShowModal(false);
      setForm(defaultFormState());
      alert('Recurring service created successfully!');
    } catch (error) {
      console.error('Error creating recurring service:', error);
      alert('Failed to create recurring service');
    } finally {
      setIsCreating(false);
    }
  };

  const handleUpdateRecurring = async (recurringId, updates) => {
    try {
      const response = await api.patch(`/recurring-services/${recurringId}`, updates);
      setRecurringServices((prev) =>
        prev.map((item) => (item.id === recurringId ? response.data : item))
      );
      alert('Recurring service updated!');
    } catch (error) {
      console.error('Error updating recurring service:', error);
      alert('Failed to update recurring service');
    }
  };

  const handleDeleteRecurring = async (recurringId) => {
    if (!window.confirm('Are you sure you want to cancel this recurring service?')) return;

    try {
      await api.delete(`/recurring-services/${recurringId}`);
      setRecurringServices((prev) => prev.filter((item) => item.id !== recurringId));
      alert('Recurring service cancelled!');
    } catch (error) {
      console.error('Error deleting recurring service:', error);
      alert('Failed to cancel recurring service');
    }
  };

  const handleMarkReminderRead = async (reminderId) => {
    try {
      await api.patch(`/recurring-services/reminders/${reminderId}/read`, { is_read: true });
      setReminders((prev) =>
        prev.map((item) => (item.id === reminderId ? { ...item, is_read: true } : item))
      );
    } catch (error) {
      console.error('Error marking reminder as read:', error);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getServiceMeta = (recurringService) => {
    if (recurringService?.service) {
      return {
        title: recurringService.service.title,
        price: recurringService.service.price,
      };
    }

    const matched = availableServices.find((service) => service.id === recurringService.service_id);
    return {
      title: matched?.title || `Service #${recurringService.service_id}`,
      price: matched?.price ?? null,
    };
  };

  if (loading) {
    return <div className="recurring-loading">Loading recurring services...</div>;
  }

  return (
    <div className="recurring-services-container">
      <div className="recurring-header">
        <h1>Recurring Services & Reminders</h1>
        <button
          className="btn btn-primary"
          onClick={() => {
            setForm(defaultFormState());
            setShowModal(true);
          }}
        >
          + Set Up Recurring Service
        </button>
      </div>

      <section className="reminders-section">
        <h2>Upcoming Reminders</h2>
        {reminders.length === 0 ? (
          <p className="empty-message">No upcoming reminders</p>
        ) : (
          <div className="reminders-list">
            {reminders.map((reminder) => (
              <div
                key={reminder.id}
                className={`reminder-card ${reminder.is_read ? 'read' : 'unread'}`}
              >
                <div className="reminder-header">
                  <span className={`reminder-badge ${reminder.reminder_type}`}>
                    {reminder.reminder_type.toUpperCase()}
                  </span>
                  <span className="reminder-status">{reminder.reminder_status}</span>
                </div>
                <p className="reminder-message">{reminder.message}</p>
                <p className="reminder-date">
                  Scheduled: {new Date(reminder.scheduled_date).toLocaleString()}
                </p>
                {!reminder.is_read && reminder.reminder_type === 'in_app' && (
                  <button
                    className="btn-small btn-secondary"
                    onClick={() => handleMarkReminderRead(reminder.id)}
                  >
                    Mark as Read
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="recurring-services-section">
        <h2>Your Recurring Services</h2>
        {recurringServices.length === 0 ? (
          <p className="empty-message">No recurring services yet. Create one to get started!</p>
        ) : (
          <div className="services-grid">
            {recurringServices.map((service) => {
              const serviceMeta = getServiceMeta(service);

              return (
                <div key={service.id} className="recurring-card">
                  <div className="card-header">
                    <h3>{serviceMeta.title}</h3>
                    <span className={`status-badge ${service.is_active ? 'active' : 'inactive'}`}>
                      {service.is_active ? 'Active' : 'Paused'}
                    </span>
                  </div>

                  <div className="card-details">
                    <p><strong>Recurrence:</strong> {service.recurrence_type}</p>
                    <p><strong>Started:</strong> {formatDate(service.start_date)}</p>
                    <p><strong>Next Service:</strong> {formatDate(service.next_booking_date)}</p>
                    {service.end_date && <p><strong>Ends:</strong> {formatDate(service.end_date)}</p>}
                    <p>
                      <strong>Price:</strong> {serviceMeta.price != null ? `INR ${serviceMeta.price}` : 'N/A'}
                    </p>
                  </div>

                  {service.notes && <p className="card-notes"><em>{service.notes}</em></p>}

                  <div className="card-actions">
                    <button
                      className="btn-small btn-secondary"
                      onClick={() => handleUpdateRecurring(service.id, { is_active: !service.is_active })}
                    >
                      {service.is_active ? 'Pause' : 'Resume'}
                    </button>
                    <button
                      className="btn-small btn-danger"
                      onClick={() => handleDeleteRecurring(service.id)}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Set Up Recurring Service</h2>
            <p>Select service and frequency to start getting reminders.</p>

            <div style={{ marginTop: '20px' }}>
              <label htmlFor="service_id">Service:</label>
              <select
                id="service_id"
                value={form.serviceId}
                onChange={(e) => setForm({ ...form, serviceId: e.target.value })}
                disabled={servicesLoading || isCreating}
              >
                <option value="">Select a service</option>
                {availableServices.map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.title} - INR {service.price}
                  </option>
                ))}
              </select>
              {servicesLoading && <p className="modal-hint">Loading services...</p>}
              {!servicesLoading && availableServices.length === 0 && (
                <p className="modal-hint">No services available right now.</p>
              )}
            </div>

            <div style={{ marginTop: '20px' }}>
              <label htmlFor="frequency">Recurrence Frequency:</label>
              <select
                id="frequency"
                value={form.recurrenceType}
                onChange={(e) => setForm({ ...form, recurrenceType: e.target.value })}
                disabled={isCreating}
              >
                <option value="weekly">Weekly</option>
                <option value="biweekly">Every 2 Weeks</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <div style={{ marginTop: '20px' }}>
              <label htmlFor="start_date">Start Date & Time:</label>
              <input
                id="start_date"
                type="datetime-local"
                value={form.startDateTime}
                onChange={(e) => setForm({ ...form, startDateTime: e.target.value })}
                disabled={isCreating}
              />
            </div>

            <div style={{ marginTop: '20px' }}>
              <label htmlFor="notes">Notes (optional):</label>
              <input
                id="notes"
                type="text"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                placeholder="Add any notes"
                disabled={isCreating}
              />
            </div>

            <div className="modal-actions">
              <button
                className="btn btn-secondary"
                onClick={() => setShowModal(false)}
                disabled={isCreating}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleCreateRecurring}
                disabled={isCreating || servicesLoading || !form.serviceId}
              >
                {isCreating ? 'Creating...' : 'Create Recurring Service'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
