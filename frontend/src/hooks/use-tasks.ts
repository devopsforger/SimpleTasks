import {useState, useEffect} from "react";
import {tasksAPI} from "@/lib/api";
import {Task} from "@/types";

export function useTasks(showAll: boolean = false) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadTasks();
  }, [showAll]);

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      const response = await tasksAPI.getTasks();
      setTasks(response.data);
    } catch (err: any) {
      setError("Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  const createTask = async (taskData: {
    title: string;
    description?: string;
    status?: string;
  }) => {
    try {
      await tasksAPI.createTask(taskData);
      await loadTasks();
      return true;
    } catch (err: any) {
      setError("Failed to create task");
      return false;
    }
  };

  const updateTask = async (
    taskId: number,
    updates: Partial<{title: string; description: string; status: string}>
  ) => {
    try {
      await tasksAPI.updateTask(taskId, updates);
      await loadTasks();
      return true;
    } catch (err: any) {
      setError("Failed to update task");
      return false;
    }
  };

  const deleteTask = async (taskId: number) => {
    try {
      await tasksAPI.deleteTask(taskId);
      await loadTasks();
      return true;
    } catch (err: any) {
      setError("Failed to delete task");
      return false;
    }
  };

  return {
    tasks,
    isLoading,
    error,
    createTask,
    updateTask,
    deleteTask,
    refreshTasks: loadTasks,
  };
}
