'use client';

import { useState } from 'react';
import { tasksAPI } from '@/lib/api';
import { Task } from '@/types';
import { Edit2, Trash2, Save, X } from 'lucide-react';

interface TaskItemProps {
  task: Task;
  onUpdate: () => void;
  onDelete: () => void;
  showActions: boolean;
}

export default function TaskItem({ task, onUpdate, onDelete, showActions }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(task.title);
  const [editedDescription, setEditedDescription] = useState(task.description);
  const [editedStatus, setEditedStatus] = useState(task.status);
  const [isLoading, setIsLoading] = useState(false);

  const handleUpdate = async () => {
    setIsLoading(true);
    try {
      await tasksAPI.updateTask(task.id, {
        title: editedTitle,
        description: editedDescription,
        status: editedStatus
      });
      setIsEditing(false);
      onUpdate();
    } catch (error) {
      console.error('Failed to update task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this task?')) {
      setIsLoading(true);
      try {
        await tasksAPI.deleteTask(task.id);
        onDelete();
      } catch (error) {
        console.error('Failed to delete task:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "status-badge";
    switch (status) {
      case 'todo': return `${baseClasses} status-todo`;
      case 'in_progress': return `${baseClasses} status-in_progress`;
      case 'done': return `${baseClasses} status-done`;
      default: return `${baseClasses} status-todo`;
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
      {isEditing ? (
        <div className="space-y-3">
          <input
            type="text"
            value={editedTitle}
            onChange={(e) => setEditedTitle(e.target.value)}
            className="input-field"
            disabled={isLoading}
          />
          <textarea
            value={editedDescription}
            onChange={(e) => setEditedDescription(e.target.value)}
            rows={2}
            className="input-field"
            disabled={isLoading}
          />
          <select
            value={editedStatus}
            onChange={(e) => setEditedStatus(e.target.value as any)}
            className="input-field"
            disabled={isLoading}
          >
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
          <div className="flex space-x-2">
            <button
              onClick={handleUpdate}
              disabled={isLoading}
              className="btn-primary flex items-center space-x-1"
            >
              <Save className="h-4 w-4" />
              <span>Save</span>
            </button>
            <button
              onClick={() => setIsEditing(false)}
              disabled={isLoading}
              className="btn-secondary flex items-center space-x-1"
            >
              <X className="h-4 w-4" />
              <span>Cancel</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex justify-between items-start">
            <h3 className="font-medium text-gray-900">{task.title}</h3>
            <span className={getStatusBadge(task.status)}>
              {task.status.replace('_', ' ')}
            </span>
          </div>

          {task.description && (
            <p className="text-gray-600 text-sm">{task.description}</p>
          )}

          <div className="flex justify-between items-center text-xs text-gray-500">
            <span>Created by: {task.owner.email}</span>
            <span>{new Date(task.created_at).toLocaleDateString()}</span>
          </div>

          {showActions && (
            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setIsEditing(true)}
                disabled={isLoading}
                className="btn-secondary flex items-center space-x-1"
              >
                <Edit2 className="h-3 w-3" />
                <span>Edit</span>
              </button>
              <button
                onClick={handleDelete}
                disabled={isLoading}
                className="btn-danger flex items-center space-x-1"
              >
                <Trash2 className="h-3 w-3" />
                <span>Delete</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}