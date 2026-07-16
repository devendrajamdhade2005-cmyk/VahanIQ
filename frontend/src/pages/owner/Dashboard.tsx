import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { useAuth } from '../../contexts/AuthContext';
import { vehicleService, Vehicle } from '../../services/vehicleService';
import { diagnosisService, Diagnosis } from '../../services/diagnosisService';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';

const OwnerDashboard: React.FC = () => {
  const { user } = useAuth();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [selectedDiagnosis, setSelectedDiagnosis] = useState<Diagnosis | null>(null);
  const [showDiagnosisModal, setShowDiagnosisModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load owner's vehicles
      const vehiclesData = await vehicleService.list({ owner_id: user?.id?.toString() });
      setVehicles(vehiclesData);

      // Load diagnoses for all owner's vehicles
      if (vehiclesData.length > 0) {
        const allDiagnoses = await Promise.all(
          vehiclesData.map(v => diagnosisService.list({ vehicle_id: v.id }))
        );
        setDiagnoses(allDiagnoses.flat());
      }

      // Select first vehicle by default
      if (vehiclesData.length > 0) {
        setSelectedVehicle(vehiclesData[0]);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthScore = (vehicle: Vehicle): { score: number; status: string; color: string } => {
    // Calculate health score based on recent diagnoses
    const vehicleDiagnoses = diagnoses.filter(d => d.vehicle_id === vehicle.id);
    
    if (vehicleDiagnoses.length === 0) {
      return { score: 100, status: 'Unknown', color: 'gray' };
    }

    const recentDiagnoses = vehicleDiagnoses.slice(0, 5);
    const criticalCount = recentDiagnoses.filter(d => d.severity === 'critical').length;
    const highCount = recentDiagnoses.filter(d => d.severity === 'high').length;
    const mediumCount = recentDiagnoses.filter(d => d.severity === 'medium').length;

    let score = 100;
    score -= criticalCount * 30;
    score -= highCount * 20;
    score -= mediumCount * 10;
    score = Math.max(0, score);

    let status = 'Excellent';
    let color = 'green';
    if (score >= 80) {
      status = 'Excellent';
      color = 'green';
    } else if (score >= 60) {
      status = 'Good';
      color = 'blue';
    } else if (score >= 40) {
      status = 'Fair';
      color = 'yellow';
    } else {
      status = 'Poor';
      color = 'red';
    }

    return { score, status, color };
  };

  const getSeverityBadge = (severity: string) => {
    const variants: Record<string, 'error' | 'warning' | 'success' | 'info'> = {
      critical: 'error',
      high: 'warning',
      medium: 'info',
      low: 'success',
    };
    return <Badge variant={variants[severity] || 'default'}>{severity.toUpperCase()}</Badge>;
  };

  const handleViewDiagnosis = (diagnosis: Diagnosis) => {
    setSelectedDiagnosis(diagnosis);
    setShowDiagnosisModal(true);
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Vehicles</h1>
          <p className="text-gray-600 mt-1">Monitor your vehicle health and service history</p>
        </div>

        {/* No Vehicles State */}
        {vehicles.length === 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
            <svg className="mx-auto h-16 w-16 text-blue-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
            </svg>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No Vehicles Yet</h2>
            <p className="text-gray-600 max-w-md mx-auto mb-4">
              You haven't added any vehicles to your account. Contact your showroom to register your vehicle.
            </p>
            <Button>Contact Showroom</Button>
          </div>
        )}

        {/* Vehicles Grid */}
        {vehicles.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {vehicles.map((vehicle) => {
                const health = getHealthScore(vehicle);
                const vehicleDiagnoses = diagnoses.filter(d => d.vehicle_id === vehicle.id);
                const pendingService = vehicleDiagnoses.filter(d => d.status === 'pending').length;

                return (
                  <div
                    key={vehicle.id}
                    className={`bg-white rounded-lg shadow-sm border-2 transition-all cursor-pointer ${
                      selectedVehicle?.id === vehicle.id
                        ? 'border-blue-500 shadow-md'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedVehicle(vehicle)}
                  >
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-bold text-gray-900">{vehicle.registration_number}</h3>
                          <p className="text-sm text-gray-600">{vehicle.make} {vehicle.model}</p>
                          <p className="text-xs text-gray-500">{vehicle.year} • {vehicle.engine_type}</p>
                        </div>
                        <div className={`h-12 w-12 rounded-full bg-${health.color}-100 flex items-center justify-center`}>
                          <span className={`text-${health.color}-600 font-bold text-sm`}>{health.score}</span>
                        </div>
                      </div>

                      <div className="space-y-2 mb-4">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Health Status</span>
                          <Badge variant={health.color === 'green' ? 'success' : health.color === 'red' ? 'error' : 'warning'}>
                            {health.status}
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Total Diagnoses</span>
                          <span className="font-medium text-gray-900">{vehicleDiagnoses.length}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Pending Services</span>
                          <span className={`font-medium ${pendingService > 0 ? 'text-yellow-600' : 'text-gray-900'}`}>
                            {pendingService}
                          </span>
                        </div>
                      </div>

                      <Button variant="outline" className="w-full" size="sm">
                        View Details
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Selected Vehicle Details */}
            {selectedVehicle && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-xl font-bold text-gray-900">
                    Service History - {selectedVehicle.registration_number}
                  </h2>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost Estimate</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {diagnoses
                        .filter(d => d.vehicle_id === selectedVehicle.id)
                        .map((diagnosis) => (
                          <tr key={diagnosis.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {new Date(diagnosis.diagnosed_at).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {diagnosis.diagnosis_type || 'General'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              {getSeverityBadge(diagnosis.severity)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Badge variant={diagnosis.status === 'completed' ? 'success' : 'warning'}>
                                {diagnosis.status.toUpperCase()}
                              </Badge>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              ₹{diagnosis.estimated_cost_min.toLocaleString()} - ₹{diagnosis.estimated_cost_max.toLocaleString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {diagnosis.estimated_time_hours}h
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <Button size="sm" variant="outline" onClick={() => handleViewDiagnosis(diagnosis)}>
                                View Report
                              </Button>
                            </td>
                          </tr>
                        ))}
                      {diagnoses.filter(d => d.vehicle_id === selectedVehicle.id).length === 0 && (
                        <tr>
                          <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                            No service history available for this vehicle.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Diagnosis Details Modal */}
      {showDiagnosisModal && selectedDiagnosis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
              <h2 className="text-2xl font-bold text-gray-900">Diagnosis Report</h2>
              <button onClick={() => setShowDiagnosisModal(false)} className="text-gray-400 hover:text-gray-600">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Overview */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Vehicle</p>
                    <p className="font-medium">{selectedDiagnosis.vehicle?.registration_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Date</p>
                    <p className="font-medium">{new Date(selectedDiagnosis.diagnosed_at).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Severity</p>
                    {getSeverityBadge(selectedDiagnosis.severity)}
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Confidence</p>
                    <p className="font-medium">{(selectedDiagnosis.confidence_score * 100).toFixed(1)}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Estimated Cost</p>
                    <p className="font-medium">
                      ₹{selectedDiagnosis.estimated_cost_min.toLocaleString()} - ₹{selectedDiagnosis.estimated_cost_max.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Estimated Time</p>
                    <p className="font-medium">{selectedDiagnosis.estimated_time_hours} hours</p>
                  </div>
                </div>
              </div>

              {/* Repair Guide */}
              {selectedDiagnosis.repair_guide && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Repair Guide</h3>
                  <div className="space-y-4">
                    {selectedDiagnosis.repair_guide.summary && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-700">{selectedDiagnosis.repair_guide.summary}</p>
                      </div>
                    )}

                    {selectedDiagnosis.repair_guide.steps && selectedDiagnosis.repair_guide.steps.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-2">Repair Steps:</p>
                        <ol className="space-y-2">
                          {selectedDiagnosis.repair_guide.steps.map((step: any, idx: number) => (
                            <li key={idx} className="flex gap-3">
                              <span className="flex-shrink-0 h-6 w-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-medium">
                                {idx + 1}
                              </span>
                              <div className="flex-1">
                                <p className="text-sm text-gray-900 font-medium">{step.title || step.description}</p>
                                {step.details && <p className="text-sm text-gray-600 mt-1">{step.details}</p>}
                              </div>
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {selectedDiagnosis.repair_guide.required_parts && selectedDiagnosis.repair_guide.required_parts.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-2">Required Parts:</p>
                        <ul className="space-y-1">
                          {selectedDiagnosis.repair_guide.required_parts.map((part: any, idx: number) => (
                            <li key={idx} className="text-sm text-gray-600 flex justify-between">
                              <span>• {part.name || part}</span>
                              {part.cost && <span className="font-medium">₹{part.cost.toLocaleString()}</span>}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 bg-gray-50">
              <div className="flex gap-3">
                <Button onClick={() => setShowDiagnosisModal(false)} variant="outline" className="flex-1">
                  Close
                </Button>
                <Button className="flex-1">Schedule Service</Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};

export default OwnerDashboard;
