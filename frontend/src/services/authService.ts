/**
 * Authentication service
 * Handles login, logout, token management, and user data
 */

import api from './api';
import { LoginCredentials, LoginResponse, User } from '../types/auth';

export const authService = {
  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/login', credentials);
    
    // Store tokens and user
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    
    return response.data;
  },

  /**
   * Logout user
   */
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  /**
   * Get current user from localStorage
   */
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  },

  /**
   * Get current user from API
   */
  async fetchCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me');
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    const user = this.getCurrentUser();
    return !!(token && user);
  },

  /**
   * Get access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  },

  /**
   * Change password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/api/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};

export default authService;
