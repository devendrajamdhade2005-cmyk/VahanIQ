/**
 * Authentication and user types
 */

export type UserRole = 'admin' | 'showroom' | 'mechanic' | 'owner';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  showroom_id: number | null;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  updateUser: (user: User) => void;
}
