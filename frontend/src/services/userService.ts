import api from './api';

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: string;
  showroom_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  showroom?: {
    id: string;
    name: string;
    location: string;
  };
}

export interface CreateUserRequest {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  role: string;
  showroom_id?: string;
}

export interface UpdateUserRequest {
  email?: string;
  full_name?: string;
  phone?: string;
  role?: string;
  showroom_id?: string;
  is_active?: boolean;
}

export const userService = {
  // List all users
  async list(params?: {
    skip?: number;
    limit?: number;
    role?: string;
    showroom_id?: string;
  }): Promise<User[]> {
    const response = await api.get('/users/', { params });
    return response.data;
  },

  // Get user by ID
  async getById(userId: string): Promise<User> {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  },

  // Create new user
  async create(data: CreateUserRequest): Promise<User> {
    const response = await api.post('/users/', data);
    return response.data;
  },

  // Update user
  async update(userId: string, data: UpdateUserRequest): Promise<User> {
    const response = await api.put(`/users/${userId}`, data);
    return response.data;
  },

  // Delete user
  async delete(userId: string): Promise<void> {
    await api.delete(`/users/${userId}`);
  },

  // Get user statistics
  async getStats(): Promise<{
    total: number;
    by_role: Record<string, number>;
    active: number;
    inactive: number;
  }> {
    const response = await api.get('/users/stats');
    return response.data;
  },
};
