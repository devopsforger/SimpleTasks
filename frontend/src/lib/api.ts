import axios from "axios";
import {Task, User} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// API methods
export const authAPI = {
  login: async (email: string, password: string) => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      console.log("Sending login data ...");

      return await api.post("/api/v1/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
    } catch (error) {
      console.log("Login API error:", error);
      throw error;
    }
  },

  register: async (
    email: string,
    password: string,
    is_admin: boolean = false
  ) => {
    try {
      console.log("Sending registration data:", {
        email,
        password,
        is_admin,
      });

      return await api.post(
        "/api/v1/auth/register",
        {
          email,
          password,
          is_admin,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
    } catch (error) {
      console.log("Registration API error:", error);
      throw error;
    }
  },
};

export const tasksAPI = {
  getTasks: (): Promise<{data: Task[]}> => api.get("/api/v1/tasks/"),
  createTask: (task: {title: string; description?: string; status?: string}) =>
    api.post("/api/v1/tasks/", task),
  updateTask: (
    id: number,
    task: Partial<{title: string; description: string; status: string}>
  ) => api.put(`/api/v1/tasks/${id}`, task),
  deleteTask: (id: number) => api.delete(`/api/v1/tasks/${id}`),
};

export const usersAPI = {
  getUsers: (): Promise<{data: User[]}> => api.get("/api/v1/users/"),
  getCurrentUser: (): Promise<{data: User}> => api.get("/api/v1/users/me"),
  updateUser: (
    id: number,
    updates: Partial<{is_active: boolean; is_admin: boolean}>
  ) => api.patch(`/api/v1/users/${id}`, updates),
  deleteUser: (id: number) => api.delete(`/api/v1/users/${id}`),
};
