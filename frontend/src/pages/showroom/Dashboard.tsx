import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { useAuth } from '../../contexts/AuthContext';
import { vehicleService, Vehicle } from '../../services/vehicleService';
import { diagnosisService, Diagnosis } from '../../services/diagnosisService';
import { userService, User } from '../../services/userService';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';

type TabType = 'overview' | 'vehicles' | 'mechanics' | 'diagnoses';

const ShowroomDashboard: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [mechanics, setMechanics] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalVehicles: 0,
    activeMechanics: 0,
    pendingDiagnoses: 0,
    completedDiagnoses: 0,
    criticalIssues: 0,
    monthlyRevenue: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load showroom-scoped data
      const showroomId = user?.showroom_id?.toString();
      
      const [vehiclesData, diagnosesData, mechanicsData] = await Promise.all([
        vehicleService.list({ showroom_id: showroomId }),
        diagnosisService.list({ limit: 100 }),
        userService.list({ role: 'mechanic', showroom_id: showroomId }),
      ]);

      setVehicles(vehiclesData);
      setDiagnoses(diagnosesData);
      setMechanics(mechanicsData);

      // Calculate stats
      const pendingCount = diagnosesData.filter(d => d.status === 'pending').length;
      const completedCount = diagnosesData.filter(d => d.status === 'completed').length;
      const criticalCount = diagnosesData.filter(d => d.severity === 'critical').length;
      
      // Calculate estimated monthly revenue
      const completedThisMonth = diagnosesData.filter(d => {
        const diagnosisDate = new Date(d.diagnosed_at);
        const now = new Date();
        return d.status === 'completed' && 
               diagnosisDate.getMonth() === now.getMonth() &&
               diagnosisDate.getFullYear() === now.getFullYear();
      });
      const monthlyRevenue = completedThisMonth.reduce((sum, d) => 
        sum + ((d.estimated_cost_min + d.estimated_cost_max) / 2), 0
      );

      setStats({
        totalVehicles: vehiclesData.length,
        activeMechanics: mechanicsData.filter(m => m.is_active).length,
        pendingDiagnoses: pendingCount,
        completedDiagnoses: completedCount,
        criticalIssues: criticalCount,
        monthlyRevenue: Math.round(monthlyRevenue),
      });
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
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
          <h1 className="text-3xl font-bold text-gray-900">Showroom Dashboard</h1>
          <p className="text-gray-600 mt-1">Manage your showroom operations</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'vehicles', label: 'Vehicles' },
              { id: 'mechanics', label: 'Mechanics' },
              { id: 'diagnoses', label: 'Diagnoses' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-600">Total Vehicles</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalVehicles}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-600">Active Mechanics</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stats.activeMechanics}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-yellow-600 mt-1">{stats.pendingDiagnoses}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-green-600 mt-1">{stats.completedDiagnoses}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-600">Critical Issues</p>
                <p className="text-2xl font-bold text-red-600 mt-1">{stats.criticalIssues}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-600">Monthly Revenue</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">₹{stats.monthlyRevenue.toLocaleString()}</p>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Diagnoses</h3>
                <div className="space-y-3">
                  {diagnoses.slice(0, 5).map((diagnosis) => (
                    <div key={diagnosis.id} className="flex items-center justify-between pb-3 border-b border-gray-100 last:border-0">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {diagnosis.vehicle?.registration_number || 'N/A'}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(diagnosis.diagnosed_at).toLocaleDateString()}
                        </p>
                      </div>
                      {getSeverityBadge(diagnosis.severity)}
                    </div>
                  ))}
                  {diagnoses.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-4">No diagnoses yet</p>
                  )}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Mechanic Performance</h3>
                <div className="space-y-3">
                  {mechanics.slice(0, 5).map((mechanic) => (
                    <div key={mechanic.id} className="flex items-center justify-between pb-3 border-b border-gray-100 last:border-0">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-blue-600 font-semibold text-sm">
                            {mechanic.full_name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{mechanic.full_name}</p>
                          <p className="text-xs text-gray-500">{mechanic.email}</p>
                        </div>
                      </div>
                      <Badge variant={mechanic.is_active ? 'success' : 'error'}>
                        {mechanic.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  ))}
                  {mechanics.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-4">No mechanics assigned</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Vehicles Tab */}
        {activeTab === 'vehicles' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Vehicles</h2>
              <Button size="sm">Add Vehicle</Button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Registration</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Make/Model</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Year</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Owner</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Engine</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {vehicles.map((vehicle) => (
                    <tr key={vehicle.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">{vehicle.registration_number}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">{vehicle.make} {vehicle.model}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{vehicle.year}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {vehicle.owner?.full_name || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{vehicle.engine_type}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        <Button size="sm" variant="outline">View</Button>
                        <Button size="sm" variant="outline">Edit</Button>
                      </td>
                    </tr>
                  ))}
                  {vehicles.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                        No vehicles found. Add a vehicle to get started.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Mechanics Tab */}
        {activeTab === 'mechanics' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Mechanics</h2>
              <Button size="sm">Add Mechanic</Button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {mechanics.map((mechanic) => (
                    <tr key={mechanic.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-blue-600 font-semibold text-sm">
                              {mechanic.full_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <span className="text-sm font-medium text-gray-900">{mechanic.full_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{mechanic.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{mechanic.phone || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant={mechanic.is_active ? 'success' : 'error'}>
                          {mechanic.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(mechanic.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        <Button size="sm" variant="outline">Edit</Button>
                      </td>
                    </tr>
                  ))}
                  {mechanics.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                        No mechanics assigned to this showroom yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Diagnoses Tab */}
        {activeTab === 'diagnoses' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">All Diagnoses</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vehicle</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost Est.</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {diagnoses.map((diagnosis) => (
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
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(diagnosis.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ₹{diagnosis.estimated_cost_min.toLocaleString()} - ₹{diagnosis.estimated_cost_max.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(diagnosis.diagnosed_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <Button size="sm" variant="outline">View</Button>
                      </td>
                    </tr>
                  ))}
                  {diagnoses.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                        No diagnoses found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default ShowroomDashboard;
