import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ClerkProvider } from '@clerk/clerk-react';
import './index.css';
import App from './App';
import LandingPage from './pages/LandingPage';

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {PUBLISHABLE_KEY ? (
      <ClerkProvider
        publishableKey={PUBLISHABLE_KEY}
        appearance={{
          variables: {
            colorPrimary: '#a68aff',
            colorTextOnPrimaryBackground: '#12082b',
            colorBackground: '#15141b',
            colorInputBackground: '#1c1a24',
            colorInputText: '#ece9f3',
            colorText: '#ece9f3',
            colorTextSecondary: '#aaa5b8',
            colorNeutral: '#ffffff',
            borderRadius: '0.5rem',
            fontFamily: "'Inter', system-ui, sans-serif",
          },
        }}
      >
        <App />
      </ClerkProvider>
    ) : (
      // No Clerk key on this deploy: show the marketing page; CTAs link to the repo.
      <LandingPage />
    )}
  </StrictMode>,
);
