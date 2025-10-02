'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import TaskForm from '@/components/features/tasks/TaskForm';
import TaskList from '@/components/features/tasks/TaskList';
import UserManagement from '@/components/features/users/UserManagement';
import { CheckSquare, Users, LogOut } from 'lucide-react';

type TabType = 'my-tasks' | 'all-tasks' | 'all-users';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('my-tasks');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleTaskUpdate = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const tabs = [
    { id: 'my-tasks' as TabType, name: 'My Tasks', icon: CheckSquare },
  ];

  if (user?.is_admin) {
    tabs.push(
      { id: 'all-tasks' as TabType, name: 'All Tasks', icon: CheckSquare },
      { id: 'all-users' as TabType, name: 'All Users', icon: Users }
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <CheckSquare className="h-8 w-8 text-blue-600" />
              <h1 className="ml-2 text-2xl font-bold text-gray-900">Task Manager</h1>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.email}
                {user?.is_admin && (
                  <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    Admin
                  </span>
                )}
              </span>
              <button
                onClick={logout}
                className="btn-secondary flex items-center space-x-2"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Task Form */}
            <div className="lg:col-span-1">
              <TaskForm onTaskCreated={handleTaskUpdate} />
            </div>

            {/* Content Area */}
            <div className="lg:col-span-2 space-y-6">
              {activeTab === 'my-tasks' && (
                <TaskList
                  key={`my-tasks-${refreshTrigger}`}
                  showAll={false}
                  onTaskUpdated={handleTaskUpdate}
                />
              )}

              {activeTab === 'all-tasks' && user?.is_admin && (
                <TaskList
                  key={`all-tasks-${refreshTrigger}`}
                  showAll={true}
                  onTaskUpdated={handleTaskUpdate}
                />
              )}

              {activeTab === 'all-users' && user?.is_admin && (
                <UserManagement key={`users-${refreshTrigger}`} />
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}