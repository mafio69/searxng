import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import ErrorBoundary from './ErrorBoundary.jsx';
import './style.css';

createRoot(document.getElementById('root')).render(<React.StrictMode><ErrorBoundary appEnv={import.meta.env?.VITE_APP_ENV}><App /></ErrorBoundary></React.StrictMode>);
