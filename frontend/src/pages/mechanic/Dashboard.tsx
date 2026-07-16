import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { diagnosisService, Diagnosis } from '../../services/diagnosisService';
import { vehicleService, Vehicle } from '../../services/vehicleService';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';

const MechanicDashboard: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [diagnosisLoading, setDiagnosisLoading] = useState(false);
  const [selectedDiagnosis, setSelectedDiagnosis] = useState<Diagnosis | null>(null);
  const [showModal, setShowModal] = useState(false);

  // Load vehicles and diagnoses on mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [vehiclesData, diagnosesData] = await Promise.all([
        vehicleService.list(),
        diagnosisService.list({ limit: 50 }),
      ]);
      setVehicles(vehiclesData);
      setDiagnoses(diagnosesData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunDiagnosis = async () => {
    if (!selectedVehicle) {
      alert('Please select a vehicle first');
      return;
    }

    setDiagnosisLoading(true);
    try {
      const newDiagnosis = await diagnosisService.create({
        vehicle_id: selectedVehicle,
      });
      
      // Refresh diagnoses list
      await loadData();
      
      // Show the new diagnosis
      setSelectedDiagnosis(newDiagnosis);
      setShowModal(true);
    } catch (error: any) {
      console.error('Error running diagnosis:', error);
      alert(error.response?.data?.detail || 'Failed to run diagnosis');
    } finally {
      setDiagnosisLoading(false);
    }
  };

  const handleViewDiagnosis = (diagnosis: Diagnosis) => {
    setSelectedDiagnosis(diagnosis);
    setShowModal(true);
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

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'success' | 'warning' | 'info' | 'default'> = {
      completed: 'success',
      in_progress: 'warning',
      pending: 'info',
    };
    return <Badge variant={variants[status] || 'default'}>{status.replace('_', ' ').toUpperCase()}</Badge>;
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
          <h1 className="text-3xl font-bold text-gray-900">Mechanic Dashboard</h1>
          <p className="text-gray-600 mt-1">AI-powered vehicle diagnostics and repair guidance</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Vehicles</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{vehicles.length}</p>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Diagnoses</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{diagnoses.length}</p>
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {diagnoses.filter(d => d.status === 'pending').length}
                </p>
              </div>
              <div className="h-12 w-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Critical Issues</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {diagnoses.filter(d => d.severity === 'critical').length}
                </p>
              </div>
              <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* AI Diagnosis Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Run AI Diagnosis</h2>
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Vehicle
              </label>
              <select
                value={selectedVehicle}
                onChange={(e) => setSelectedVehicle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Choose a vehicle...</option>
                {vehicles.map((vehicle) => (
                  <option key={vehicle.id} value={vehicle.id}>
                    {vehicle.registration_number} - {vehicle.make} {vehicle.model} ({vehicle.year})
                  </option>
                ))}
              </select>
            </div>
            <Button
              onClick={handleRunDiagnosis}
              disabled={!selectedVehicle || diagnosisLoading}
              className="whitespace-nowrap"
            >
              {diagnosisLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Running Diagnosis...
                </>
              ) : (
                'Run Diagnosis'
              )}
            </Button>
          </div>
        </div>

        {/* Recent Diagnoses */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Recent Diagnoses</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vehicle
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Severity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {diagnoses.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                      No diagnoses found. Run a diagnosis to get started.
                    </td>
                  </tr>
                ) : (
                  diagnoses.map((diagnosis) => (
                    <tr key={diagnosis.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {diagnosis.vehicle?.registration_number || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {diagnosis.vehicle?.make} {diagnosis.vehicle?.model}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {diagnosis.diagnosis_type || 'General'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getSeverityBadge(diagnosis.severity)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {(diagnosis.confidence_score * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(diagnosis.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(diagnosis.diagnosed_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleViewDiagnosis(diagnosis)}
                        >
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Diagnosis Details Modal */}
      {showModal && selectedDiagnosis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
              <h2 className="text-2xl font-bold text-gray-900">Diagnosis Details</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Overview */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Overview</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Vehicle</p>
                    <p className="font-medium">{selectedDiagnosis.vehicle?.registration_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Type</p>
                    <p className="font-medium">{selectedDiagnosis.diagnosis_type || 'General'}</p>
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

              {/* ML Prediction */}
              {selectedDiagnosis.ml_prediction && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">ML Prediction</h3>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-700">
                      <strong>Predicted Issue:</strong> {selectedDiagnosis.ml_prediction.predicted_class || 'N/A'}
                    </p>
                    {selectedDiagnosis.ml_prediction.explanation && (
                      <p className="text-sm text-gray-700 mt-2">
                        <strong>Explanation:</strong> {selectedDiagnosis.ml_prediction.explanation}
                      </p>
                    )}
                    {selectedDiagnosis.ml_prediction.top_features && (
                      <div className="mt-3">
                        <p className="text-sm font-medium text-gray-700 mb-2">Key Indicators:</p>
                        <ul className="space-y-1">
                          {selectedDiagnosis.ml_prediction.top_features.slice(0, 5).map((feature: any, idx: number) => (
                            <li key={idx} className="text-sm text-gray-600">
                              • {feature.feature}: {feature.value} (impact: {feature.contribution > 0 ? '+' : ''}{feature.contribution.toFixed(3)})
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* RAG Context */}
              {selectedDiagnosis.rag_context && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Knowledge Base Context</h3>
                  {selectedDiagnosis.rag_context.relevant_articles && selectedDiagnosis.rag_context.relevant_articles.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Relevant Articles:</p>
                      <ul className="space-y-2">
                        {selectedDiagnosis.rag_context.relevant_articles.map((article: any, idx: number) => (
                          <li key={idx} className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                            <p className="font-medium text-gray-900">{article.title || `Article ${idx + 1}`}</p>
                            <p className="mt-1">{article.content?.substring(0, 200)}...</p>
                            <p className="text-xs text-gray-500 mt-1">Relevance: {(article.score * 100).toFixed(1)}%</p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {selectedDiagnosis.rag_context.similar_cases && selectedDiagnosis.rag_context.similar_cases.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Similar Cases:</p>
                      <ul className="space-y-2">
                        {selectedDiagnosis.rag_context.similar_cases.map((case_: any, idx: number) => (
                          <li key={idx} className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                            <p className="font-medium text-gray-900">{case_.title || `Case ${idx + 1}`}</p>
                            <p className="mt-1">{case_.summary || case_.content?.substring(0, 150)}...</p>
                            <p className="text-xs text-gray-500 mt-1">Similarity: {(case_.similarity * 100).toFixed(1)}%</p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Repair Guide */}
              {selectedDiagnosis.repair_guide && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">AI Repair Guide</h3>
                  <div className="space-y-4">
                    {selectedDiagnosis.repair_guide.summary && (
                      <div className="bg-green-50 p-4 rounded-lg">
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
                                {step.duration && <p className="text-xs text-gray-500 mt-1">Duration: {step.duration}</p>}
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

                    {selectedDiagnosis.repair_guide.safety_warnings && selectedDiagnosis.repair_guide.safety_warnings.length > 0 && (
                      <div className="bg-yellow-50 p-4 rounded-lg">
                        <p className="text-sm font-medium text-yellow-800 mb-2">⚠️ Safety Warnings:</p>
                        <ul className="space-y-1">
                          {selectedDiagnosis.repair_guide.safety_warnings.map((warning: string, idx: number) => (
                            <li key={idx} className="text-sm text-yellow-700">• {warning}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 bg-gray-50 sticky bottom-0">
              <Button onClick={() => setShowModal(false)} variant="outline" className="w-full">
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};

export default MechanicDashboard;
