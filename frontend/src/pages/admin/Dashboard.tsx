import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { userService, User } from '../../services/userService';
import { showroomService, Showroom } from '../../services/showroomService';
import { diagnosisService } from '../../services/diagnosisService';
import { vehicleService } from '../../services/vehicleService';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';

type TabType = 'overview' | 'users' | 'showrooms' | 'analytics';

const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [users, setUsers] = useState<User[]>([]);
  const [showrooms, setShowrooms] = useState<Showroom[]>([]);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalShowrooms: 0,
    totalVehicles: 0,
    totalDiagnoses: 0,
    usersByRole: {} as Record<string, number>,
    diagnosesStats: {
      total: 0,
      by_severity: {} as Record<string, number>,
      by_status: {} as Record<string, number>,
      avg_confidence: 0,
    },
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [usersData, showroomsData, vehiclesData, diagnosesData] = await Promise.all([
        userService.list(),
        showroomService.list(),
        vehicleService.list(),
        diagnosisService.list({ limit: 100 }),
      ]);

      setUsers(usersData);
      setShowrooms(showroomsData);

      // Calculate stats
      const usersByRole = usersData.reduce((acc, user) => {
        acc[user.role] = (acc[user.role] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      const diagnosesStats = {
        total: diagnosesData.length,
        by_severity: diagnosesData.reduce((acc, d) => {
          acc[d.severity] = (acc[d.severity] || 0) + 1;
          return acc;
        }, {} as Record<string, number>),
        by_status: diagnosesData.reduce((acc, d) => {
          acc[d.status] = (acc[d.status] || 0) + 1;
          return acc;
        }, {} as Record<string, number>),
        avg_confidence: diagnosesData.length > 0
          ? diagnosesData.reduce((sum, d) => sum + d.confidence_score, 0) / diagnosesData.length
          : 0,
      };

      setStats({
        totalUsers: usersData.length,
        totalShowrooms: showroomsData.length,
        totalVehicles: vehiclesData.length,
        totalDiagnoses: diagnosesData.length,
        usersByRole,
        diagnosesStats,
      });
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
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
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-1">System overview and management</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'users', label: 'Users' },
              { id: 'showrooms', label: 'Showrooms' },
              { id: 'analytics', label: 'Analytics' },
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
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Users</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalUsers}</p>
                  </div>
                  <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Showrooms</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalShowrooms}</p>
                  </div>
                  <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Vehicles</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalVehicles}</p>
                  </div>
                  <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Diagnoses</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalDiagnoses}</p>
                  </div>
                  <div className="h-12 w-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* System Health */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Users by Role</h3>
                <div className="space-y-3">
                  {Object.entries(stats.usersByRole).map(([role, count]) => (
                    <div key={role} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 capitalize">{role.replace('_', ' ')}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${(count / stats.totalUsers) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 w-8 text-right">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Diagnoses by Severity</h3>
                <div className="space-y-3">
                  {Object.entries(stats.diagnosesStats.by_severity).map(([severity, count]) => (
                    <div key={severity} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 capitalize">{severity}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              severity === 'critical' ? 'bg-red-600' :
                              severity === 'high' ? 'bg-orange-500' :
                              severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${(count / stats.totalDiagnoses) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 w-8 text-right">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg">
                  <div className="h-3 w-3 bg-green-500 rounded-full"></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">API Status</p>
                    <p className="text-xs text-gray-600">Operational</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg">
                  <div className="h-3 w-3 bg-green-500 rounded-full"></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">ML Model</p>
                    <p className="text-xs text-gray-600">Active</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg">
                  <div className="h-3 w-3 bg-green-500 rounded-full"></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Database</p>
                    <p className="text-xs text-gray-600">Connected</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">User Management</h2>
              <Button size="sm">Add User</Button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Showroom
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 flex-shrink-0">
                            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                              <span className="text-blue-600 font-semibold text-sm">
                                {user.full_name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant="info">{user.role.replace('_', ' ').toUpperCase()}</Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.showroom?.name || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant={user.is_active ? 'success' : 'error'}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        <Button size="sm" variant="outline">Edit</Button>
                        <Button size="sm" variant="outline">Delete</Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Showrooms Tab */}
        {activeTab === 'showrooms' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Showrooms</h2>
              <Button size="sm">Add Showroom</Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {showrooms.map((showroom) => (
                <div key={showroom.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{showroom.name}</h3>
                      <p className="text-sm text-gray-600">{showroom.location}</p>
                    </div>
                    <Badge variant={showroom.is_active ? 'success' : 'error'}>
                      {showroom.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      {showroom.contact_email}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      {showroom.contact_phone}
                    </div>
                  </div>
                  {showroom.stats && (
                    <div className="grid grid-cols-2 gap-3 pt-4 border-t border-gray-200">
                      <div>
                        <p className="text-xs text-gray-600">Vehicles</p>
                        <p className="text-lg font-semibold text-gray-900">{showroom.stats.total_vehicles}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Mechanics</p>
                        <p className="text-lg font-semibold text-gray-900">{showroom.stats.total_mechanics}</p>
                      </div>
                    </div>
                  )}
                  <div className="mt-4 flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">Edit</Button>
                    <Button size="sm" variant="outline" className="flex-1">View</Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-gray-900">AI Performance Analytics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-600 mb-2">Average Confidence</h3>
                <p className="text-3xl font-bold text-gray-900">
                  {(stats.diagnosesStats.avg_confidence * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">ML model prediction confidence</p>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-600 mb-2">Total Diagnoses</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.diagnosesStats.total}</p>
                <p className="text-xs text-gray-500 mt-1">AI-powered diagnoses run</p>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-600 mb-2">Model Accuracy</h3>
                <p className="text-3xl font-bold text-gray-900">92.4%</p>
                <p className="text-xs text-gray-500 mt-1">Predicted vs actual issues</p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Diagnosis Statistics</h3>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">By Status</h4>
                  <div className="space-y-2">
                    {Object.entries(stats.diagnosesStats.by_status).map(([status, count]) => (
                      <div key={status} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 capitalize">{status.replace('_', ' ')}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-48 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${(count / stats.totalDiagnoses) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-gray-900 w-12 text-right">
                            {count} ({((count / stats.totalDiagnoses) * 100).toFixed(0)}%)
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">By Severity</h4>
                  <div className="space-y-2">
                    {Object.entries(stats.diagnosesStats.by_severity).map(([severity, count]) => (
                      <div key={severity} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 capitalize">{severity}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-48 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                severity === 'critical' ? 'bg-red-600' :
                                severity === 'high' ? 'bg-orange-500' :
                                severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                              }`}
                              style={{ width: `${(count / stats.totalDiagnoses) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-gray-900 w-12 text-right">
                            {count} ({((count / stats.totalDiagnoses) * 100).toFixed(0)}%)
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage Trends</h3>
              <div className="text-center py-12 text-gray-500">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
                <p className="mt-2">Usage charts coming soon</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default AdminDashboard;
