import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '../api/client';
import { User } from '../user';

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  checkAuth: (initData: string) => Promise<void>;
  login: (telegramData: any) => Promise<void>;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      checkAuth: async (initData: string) => {
        set({ isLoading: true, error: null });
        
        try {
          // Parse initData to get user info
          const params = new URLSearchParams(initData);
          const userJson = params.get('user');
          
          if (!userJson) {
            throw new Error('No user data in initData');
          }
          
          const telegramUser = JSON.parse(userJson);
          
          // Authenticate with backend
          const response = await api.post('/auth/telegram', {
            ...telegramUser,
            auth_date: parseInt(params.get('auth_date') || '0'),
            hash: params.get('hash'),
          });
          
          const { token, user } = response.data;
          
          // Set token in API client
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          set({
            token,
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Authentication failed',
            isAuthenticated: false,
          });
        }
      },

      login: async (telegramData: any) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await api.post('/auth/telegram', telegramData);
          const { token, user } = response.data;
          
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          set({
            token,
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Login failed',
          });
        }
      },

      logout: () => {
        delete api.defaults.headers.common['Authorization'];
        set({
          token: null,
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },

      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({
            user: { ...currentUser, ...userData },
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);
