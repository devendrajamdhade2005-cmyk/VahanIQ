import api from './api';

export interface Showroom {
  id: string;
  name: string;
  location: string;
  contact_email: string;
  contact_phone: string;
  address?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  stats?: {
    total_vehicles: number;
    total_mechanics: number;
    pending_diagnoses: number;
    total_revenue: number;
  };
}

export interface CreateShowroomRequest {
  name: string;
  location: string;
  contact_email: string;
  contact_phone: string;
  address?: string;
}

export interface UpdateShowroomRequest {
  name?: string;
  location?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  is_active?: boolean;
}

export const showroomService = {
  // List all showrooms
  async list(params?: {
    skip?: number;
    limit?: number;
    is_active?: boolean;
  }): Promise<Showroom[]> {
    const response = await api.get('/showrooms/', { params });
    return response.data;
  },

  // Get showroom by ID
  async getById(showroomId: string): Promise<Showroom> {
    const response = await api.get(`/showrooms/${showroomId}`);
    return response.data;
  },

  // Create new showroom
  async create(data: CreateShowroomRequest): Promise<Showroom> {
    const response = await api.post('/showrooms/', data);
    return response.data;
  },

  // Update showroom
  async update(showroomId: string, data: UpdateShowroomRequest): Promise<Showroom> {
    const response = await api.put(`/showrooms/${showroomId}`, data);
    return response.data;
  },

  // Delete showroom
  async delete(showroomId: string): Promise<void> {
    await api.delete(`/showrooms/${showroomId}`);
  },

  // Get showroom statistics
  async getStats(showroomId: string): Promise<{
    total_vehicles: number;
    total_mechanics: number;
    pending_diagnoses: number;
    completed_diagnoses: number;
    total_revenue: number;
    monthly_revenue: number;
  }> {
    const response = await api.get(`/showrooms/${showroomId}/stats`);
    return response.data;
  },
};
