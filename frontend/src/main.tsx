import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import './core/i18n/i18n';
import { telemetry } from './core/observability/telemetry';
import { registerSW } from 'virtual:pwa-register';

// Registro automático del Service Worker para capacidades PWA y resiliencia offline
registerSW({ immediate: true });

// Inicialización de Observabilidad Forense de Usuario Real (RUM)
telemetry.init({
  appName: 'ateneo-frontend',
  appVersion: '1.0.0',
  sampleRate: 1.0
});

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Elemento root no encontrado en el DOM.');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
