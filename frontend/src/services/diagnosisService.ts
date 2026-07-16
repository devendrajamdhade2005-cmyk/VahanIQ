import api from './api';

export interface Diagnosis {
  id: string;
  vehicle_id: string;
  diagnosis_type: string;
  severity: string;
  confidence_score: number;
  ml_prediction: any;
  rag_context: any;
  repair_guide: any;
  estimated_cost_min: number;
  estimated_cost_max: number;
  estimated_time_hours: number;
  status: string;
  diagnosed_at: string;
  vehicle?: {
    registration_number: string;
    make: string;
    model: string;
    year: number;
  };
}

export interface CreateDiagnosisRequest {
  vehicle_id: string;
  diagnosis_type?: string;
}

export const diagnosisService = {
  // List all diagnoses
  async list(params?: {
    skip?: number;
    limit?: number;
    vehicle_id?: string;
    status?: string;
  }): Promise<Diagnosis[]> {
    const response = await api.get('/diagnoses/', { params });
    return response.data;
  },

  // Get diagnosis by ID
  async getById(diagnosisId: string): Promise<Diagnosis> {
    const response = await api.get(`/diagnoses/${diagnosisId}`);
    return response.data;
  },

  // Create new diagnosis (trigger AI pipeline)
  async create(data: CreateDiagnosisRequest): Promise<Diagnosis> {
    const response = await api.post('/diagnoses/', data);
    return response.data;
  },

  // Update diagnosis
  async update(diagnosisId: string, data: Partial<Diagnosis>): Promise<Diagnosis> {
    const response = await api.put(`/diagnoses/${diagnosisId}`, data);
    return response.data;
  },

  // Delete diagnosis
  async delete(diagnosisId: string): Promise<void> {
    await api.delete(`/diagnoses/${diagnosisId}`);
  },

  // Get diagnosis statistics
  async getStats(): Promise<{
    total: number;
    by_severity: Record<string, number>;
    by_status: Record<string, number>;
    avg_confidence: number;
  }> {
    const response = await api.get('/diagnoses/stats');
    return response.data;
  },
};
