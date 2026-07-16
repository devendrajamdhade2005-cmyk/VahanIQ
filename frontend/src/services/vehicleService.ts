import api from './api';

export interface Vehicle {
  id: string;
  registration_number: string;
  make: string;
  model: string;
  year: number;
  vin?: string;
  engine_type: string;
  transmission_type: string;
  fuel_type: string;
  owner_id?: string;
  showroom_id?: string;
  created_at: string;
  updated_at: string;
  owner?: {
    id: string;
    full_name: string;
    email: string;
    phone?: string;
  };
}

export interface CreateVehicleRequest {
  registration_number: string;
  make: string;
  model: string;
  year: number;
  vin?: string;
  engine_type: string;
  transmission_type: string;
  fuel_type: string;
  owner_id?: string;
  showroom_id?: string;
}

export const vehicleService = {
  // List all vehicles
  async list(params?: {
    skip?: number;
    limit?: number;
    owner_id?: string;
    showroom_id?: string;
  }): Promise<Vehicle[]> {
    const response = await api.get('/vehicles/', { params });
    return response.data;
  },

  // Get vehicle by ID
  async getById(vehicleId: string): Promise<Vehicle> {
    const response = await api.get(`/vehicles/${vehicleId}`);
    return response.data;
  },

  // Create new vehicle
  async create(data: CreateVehicleRequest): Promise<Vehicle> {
    const response = await api.post('/vehicles/', data);
    return response.data;
  },

  // Update vehicle
  async update(vehicleId: string, data: Partial<CreateVehicleRequest>): Promise<Vehicle> {
    const response = await api.put(`/vehicles/${vehicleId}`, data);
    return response.data;
  },

  // Delete vehicle
  async delete(vehicleId: string): Promise<void> {
    await api.delete(`/vehicles/${vehicleId}`);
  },

  // Get vehicle health summary
  async getHealthSummary(vehicleId: string): Promise<{
    overall_health: string;
    recent_issues: number;
    last_diagnosis: string | null;
  }> {
    const response = await api.get(`/vehicles/${vehicleId}/health`);
    return response.data;
  },
};
