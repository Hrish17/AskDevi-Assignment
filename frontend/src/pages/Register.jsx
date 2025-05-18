import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Register.css';

const API_BASE = 'http://localhost:8000/api';

const Register = () => {
    const navigate = useNavigate();

    const [form, setForm] = useState({
        name: '',
        dateOfBirth: '',
        timeOfBirth: '',
        placeOfBirth: '',
    });
    const [errors, setErrors] = useState({});
    const [apiError, setApiError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = e => {
        setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
        setErrors(prev => ({ ...prev, [e.target.name]: '' }));
    };

    const validate = () => {
        const newErrors = {};
        if (!form.name.trim()) newErrors.name = 'Name is required';
        if (!form.dateOfBirth) newErrors.dateOfBirth = 'Date of birth is required';
        if (!form.timeOfBirth) newErrors.timeOfBirth = 'Time of birth is required';
        if (!form.placeOfBirth.trim()) newErrors.placeOfBirth = 'Place of birth is required';
        return newErrors;
    };

    const handleSubmit = async e => {
        e.preventDefault();
        setApiError('');
        const validationErrors = validate();
        if (Object.keys(validationErrors).length) {
            setErrors(validationErrors);
            return;
        }

        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: form.name,
                    date_of_birth: form.dateOfBirth,
                    time_of_birth: form.timeOfBirth,
                    place_of_birth: form.placeOfBirth
                })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Failed to register');
            }

            const { session_id } = await res.json();

            // Persist for later use in Chat.jsx
            localStorage.setItem('birthDetails', JSON.stringify(form));
            localStorage.setItem('sessionId', session_id);

            navigate('/chat');
        } catch (err) {
            console.error(err);
            setApiError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-container">
            <h2>Enter Your Birth Details</h2>
            <form onSubmit={handleSubmit} className="register-form" noValidate>
                {apiError && <div className="api-error">{apiError}</div>}

                <label>
                    Name
                    <input
                        type="text"
                        name="name"
                        value={form.name}
                        onChange={handleChange}
                        placeholder="Your full name"
                        disabled={loading}
                    />
                    {errors.name && <span className="error">{errors.name}</span>}
                </label>

                <label>
                    Date of Birth
                    <input
                        type="date"
                        name="dateOfBirth"
                        value={form.dateOfBirth}
                        onChange={handleChange}
                        disabled={loading}
                    />
                    {errors.dateOfBirth && <span className="error">{errors.dateOfBirth}</span>}
                </label>

                <label>
                    Time of Birth
                    <input
                        type="time"
                        name="timeOfBirth"
                        value={form.timeOfBirth}
                        onChange={handleChange}
                        disabled={loading}
                    />
                    {errors.timeOfBirth && <span className="error">{errors.timeOfBirth}</span>}
                </label>

                <label>
                    Place of Birth
                    <input
                        type="text"
                        name="placeOfBirth"
                        value={form.placeOfBirth}
                        onChange={handleChange}
                        placeholder="City, State"
                        disabled={loading}
                    />
                    {errors.placeOfBirth && <span className="error">{errors.placeOfBirth}</span>}
                </label>

                <button type="submit" disabled={loading}>
                    {loading ? 'Saving…' : 'Save & Continue'}
                </button>
            </form>
        </div>
    );
};

export default Register;
