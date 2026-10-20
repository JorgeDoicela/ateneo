import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../../modules/auth/api/authApi';
import type { User } from '../../types';

export interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  sessionConsentAcknowledged: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  verifyAuth: () => Promise<void>;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setAuth: (user: User, token: string) => void;
  setSessionConsentAcknowledged: (acknowledged: boolean) => void;
  acceptTermsAndUnlockSession: (version?: string) => Promise<User>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      loading: true,
      sessionConsentAcknowledged: typeof sessionStorage !== 'undefined' 
        ? sessionStorage.getItem('ateneo_session_consent_acknowledged') === 'true' 
        : false,

      setUser: (user) => set({ user }),
      setToken: (token) => {
        if (typeof localStorage !== 'undefined') {
          if (token) {
            localStorage.setItem('ateneo_token', token);
          } else {
            localStorage.removeItem('ateneo_token');
          }
        }
        set({ token });
      },
      setAuth: (user, token) => {
        if (typeof localStorage !== 'undefined') {
          localStorage.setItem('ateneo_token', token);
        }
        set({ user, token, loading: false });
      },

      setSessionConsentAcknowledged: (acknowledged: boolean) => {
        if (typeof sessionStorage !== 'undefined') {
          if (acknowledged) {
            sessionStorage.setItem('ateneo_session_consent_acknowledged', 'true');
          } else {
            sessionStorage.removeItem('ateneo_session_consent_acknowledged');
          }
        }
        set({ sessionConsentAcknowledged: acknowledged });
      },

      acceptTermsAndUnlockSession: async (version?: string): Promise<User> => {
        const updatedUser = await authApi.acceptTerms(version);
        if (typeof sessionStorage !== 'undefined') {
          sessionStorage.setItem('ateneo_session_consent_acknowledged', 'true');
        }
        set({ user: updatedUser, sessionConsentAcknowledged: true });
        return updatedUser;
      },

      login: async (email: string, password: string): Promise<User> => {
        set({ loading: true });
        try {
          const data = await authApi.login(email, password);
          if (typeof localStorage !== 'undefined') {
            localStorage.setItem('ateneo_token', data.access_token);
          }
          if (typeof sessionStorage !== 'undefined') {
            sessionStorage.removeItem('ateneo_session_consent_acknowledged');
          }
          set({
            token: data.access_token,
            user: data.user,
            loading: false,
            sessionConsentAcknowledged: false,
          });
          return data.user;
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } catch (err) {
          console.warn('Revocación de sesión en servidor completada localmente:', err);
        } finally {
          if (typeof localStorage !== 'undefined') {
            localStorage.removeItem('ateneo_token');
          }
          if (typeof sessionStorage !== 'undefined') {
            sessionStorage.removeItem('ateneo_session_consent_acknowledged');
          }
          set({
            user: null,
            token: null,
            loading: false,
            sessionConsentAcknowledged: false,
          });
        }
      },

      verifyAuth: async () => {
        const currentToken = get().token || (typeof localStorage !== 'undefined' ? localStorage.getItem('ateneo_token') : null);
        if (!currentToken) {
          set({ user: null, token: null, loading: false });
          return;
        }

        try {
          const userData = await authApi.getMe();
          set({
            user: userData,
            token: currentToken,
            loading: false,
          });
        } catch (err) {
          console.error('Sesión expirada o token inválido:', err);
          get().logout();
        }
      },
    }),
    {
      name: 'ateneo_auth_session',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
      }),
    }
  )
);

export default useAuthStore;
