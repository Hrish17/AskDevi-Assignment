import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/Chat.css';
import deviLogo from '../assets/devi.webp';
import domain from "../domain";

const Chat = () => {
    const navigate = useNavigate();
    const [birthDetails, setBirthDetails] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    const [chatHistory, setChatHistory] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const chatEndRef = useRef(null);

    useEffect(() => {
        const bd = localStorage.getItem('birthDetails');
        const sid = localStorage.getItem('sessionId');
        if (!bd || !sid) {
            navigate('/register');
        } else {
            setBirthDetails(JSON.parse(bd));
            setSessionId(sid);
        }
    }, [navigate]);

    useEffect(() => {
        if (!sessionId) return;

        fetch(`${domain}/chat-history/${sessionId}/`)
            .then(res => {
                if (!res.ok) throw new Error('Failed to load chat history');
                return res.json();
            })
            .then(data => {
                const formattedHistory = data.flatMap(msg => [
                    { sender: 'user', text: msg.user_message },
                    { sender: 'bot', text: msg.devi_response }
                ]);

                console.log("Formatted chat history:", formattedHistory);
                setChatHistory(formattedHistory);
            })
            .catch(err => {
                console.error("Chat history fetch error:", err);
                setError(err.message || 'Could not load chat history');
            });
    }, [sessionId]);


    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory, loading]);

    const logout = () => {
        localStorage.clear();
        navigate('/');
    };

    const sendMessage = () => {
        if (!input.trim() || loading) return;
        setError('');
        setLoading(true);

        const userMsg = { sender: 'user', text: input.trim() };
        setChatHistory(prev => [...prev, userMsg]);

        fetch(`${domain}/chat/${sessionId}/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: input.trim() })
        })
            .then(res => {
                if (!res.ok) return res.json().then(err => Promise.reject(err));
                return res.json();
            })
            .then(({ answer }) => {
                const botMsg = { sender: 'bot', text: answer };
                setChatHistory(prev => [...prev, botMsg]);
            })
            .catch(err => {
                console.error(err);
                setError(err.error || 'Failed to send message');
            })
            .finally(() => {
                setLoading(false);
                setInput('');
            });
    };

    const handleKeyDown = e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="chat-page">
            <nav className="chat-navbar">
                <Link to="/" className="logo gradient-text">
                    <div className="left-section">
                        <img src={deviLogo} alt="Devi Logo" className="devi-logo" />
                        <span className="askdevi-logo-text">Ask Devi</span>
                    </div>
                </Link>
                <div className="right-section">
                    <Link to="/update" className="nav-btn logout-btn">Edit Birth Details</Link>
                    <button onClick={logout} className="nav-btn logout-btn">Logout</button>
                </div>
            </nav>

            <div className="chat-container">

                <div className="chat-history">
                    {chatHistory.length === 0 && !error && (
                        <div className="empty-text">Ask your first question!</div>
                    )}
                    {chatHistory.map((msg, i) => (
                        <div
                            key={i}
                            className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}
                        >
                            {msg.text}
                        </div>
                    ))}

                    {loading && (
                        <div className="typing-indicator">
                            <span className="dot"></span>
                            <span className="dot"></span>
                            <span className="dot"></span>
                        </div>
                    )}

                    <div ref={chatEndRef} />
                </div>

                {error && <div className="error-banner">{error}</div>}

                <div className="chat-input-container">
                    <textarea
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Type your question..."
                        rows={2}
                        disabled={loading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={loading || !input.trim()}
                    >
                        {loading ? 'Thinking…' : 'Send'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Chat;
