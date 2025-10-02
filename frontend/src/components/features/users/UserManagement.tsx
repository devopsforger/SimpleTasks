'use client';

import { useState, useEffect } from 'react';
import { usersAPI } from '@/lib/api';
import { User } from '@/types';

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await usersAPI.getUsers();
      setUsers(response.data);
    } catch (err: any) {
      setError('Failed to load users');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAdminStatus = async (userId: number, currentStatus: boolean) => {
    try {
      await usersAPI.updateUser(userId, { is_admin: !currentStatus });
      loadUsers(); // Reload the list
    } catch (err: any) {
      setError('Failed to update user');
    }
  };

  const deleteUser = async (userId: number, userEmail: string) => {
    if (confirm(`Are you sure you want to delete user ${userEmail}?`)) {
      try {
        await usersAPI.deleteUser(userId);
        loadUsers(); // Reload the list
      } catch (err: any) {
        setError('Failed to delete user');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">User Management</h2>

      {error && (
        <div className="rounded-md bg-red-50 p-4 mb-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      {users.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No users found</p>
      ) : (
        <div className="space-y-4">
          {users.map((user) => (
            <div key={user.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium text-gray-900">{user.email}</h3>
                  <div className="flex space-x-2 text-sm text-gray-500 mt-1">
                    <span>ID: {user.id}</span>
                    <span>•</span>
                    <span className={user.is_active ? 'text-green-600' : 'text-red-600'}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <span>•</span>
                    <span className={user.is_admin ? 'text-blue-600' : 'text-gray-600'}>
                      {user.is_admin ? 'Admin' : 'User'}
                    </span>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => toggleAdminStatus(user.id, user.is_admin)}
                    className={`${user.is_admin ? 'btn-secondary' : 'btn-primary'
                      } text-sm`}
                  >
                    {user.is_admin ? 'Remove Admin' : 'Make Admin'}
                  </button>

                  <button
                    onClick={() => deleteUser(user.id, user.email)}
                    className="btn-danger text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}