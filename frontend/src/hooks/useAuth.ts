import { create } from 'zustand';
import { api } from '../services/api';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'enterprise' | 'admin';
  organization_id?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, fullName: string, orgId?: string) => Promise<boolean>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuth = create<AuthState>((set) => {
  // Lắng nghe sự kiện hết hạn token từ interceptor
  if (typeof window !== 'undefined') {
    window.addEventListener('auth_session_expired', () => {
      set({ user: null, isAuthenticated: false, error: 'Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.' });
    });
  }

  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,

    clearError: () => set({ error: null }),

    login: async (email, password) => {
      set({ isLoading: true, error: null });
      try {
        const response = await api.post('/auth/login', { email, password });
        const { access_token, refresh_token, user } = response.data;

        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        set({ user, isAuthenticated: true, isLoading: false });
        return true;
      } catch (err: any) {
        let errMsg = 'Đăng nhập thất bại. Vui lòng kiểm tra lại email/mật khẩu.';
        if (!err.response) {
          errMsg = 'Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại kết nối mạng.';
        } else if (err.response.data?.detail) {
          errMsg = typeof err.response.data.detail === 'string' 
            ? err.response.data.detail 
            : 'Đăng nhập thất bại. Vui lòng thử lại.';
        }
        
        set({ error: errMsg, isLoading: false });
        return false;
      }
    },

    register: async (email, password, fullName, orgId) => {
      set({ isLoading: true, error: null });
      try {
        await api.post('/auth/register', {
          email,
          password,
          full_name: fullName,
          organization_id: orgId || null,
        });
        set({ isLoading: false });
        return true;
      } catch (err: any) {
        let errMsg = 'Đăng ký thất bại. Vui lòng thử lại sau.';
        if (!err.response) {
          errMsg = 'Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại kết nối mạng.';
        } else if (err.response.data?.detail) {
          errMsg = Array.isArray(err.response.data.detail)
            ? 'Thông tin không hợp lệ, vui lòng kiểm tra lại.'
            : err.response.data.detail;
        } else if (err.response.status === 409) {
          errMsg = 'Email có thể đã tồn tại.';
        }
        
        set({ error: errMsg, isLoading: false });
        return false;
      }
    },

    logout: () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false, error: null });
    },

    checkAuth: async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        set({ user: null, isAuthenticated: false, isLoading: false });
        return;
      }

      set({ isLoading: true });
      try {
        const response = await api.get('/auth/me');
        set({ user: response.data, isAuthenticated: true, isLoading: false });
      } catch (err) {
        // Token có thể hết hạn và tự động refresh thất bại
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    },
  };
});
