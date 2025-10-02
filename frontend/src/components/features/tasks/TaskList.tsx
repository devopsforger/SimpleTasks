'use client';

import { useState, useEffect } from 'react';
import { tasksAPI } from '@/lib/api';
import { Task } from '@/types';
import TaskItem from './TaskItem';

interface TaskListProps {
  showAll: boolean;
  onTaskUpdated: () => void;
}

export default function TaskList({ showAll, onTaskUpdated }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTasks();
  }, [showAll]);

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      const response = await tasksAPI.getTasks();
      setTasks(response.data);
    } catch (err: any) {
      setError('Failed to load tasks');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTaskUpdate = () => {
    loadTasks();
    onTaskUpdated();
  };

  const handleTaskDelete = () => {
    loadTasks();
    onTaskUpdated();
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
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        {showAll ? 'All Tasks' : 'My Tasks'}
      </h2>

      {error && (
        <div className="rounded-md bg-red-50 p-4 mb-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      {tasks.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No tasks found</p>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onUpdate={handleTaskUpdate}
              onDelete={handleTaskDelete}
              showActions={true}
            />
          ))}
        </div>
      )}
    </div>
  );
}