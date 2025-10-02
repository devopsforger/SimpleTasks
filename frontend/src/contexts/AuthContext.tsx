'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import { getStoredAuth } from '@/lib/auth';
import { User, AuthContextType } from '@/types';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const auth = getStoredAuth();
    if (auth) {
      setUser(auth.user);
      setToken(auth.token);
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await authAPI.login(email, password);
      const { access_token, user_id, is_admin } = response.data;

      const userData: User = {
        id: user_id,
        email,
        is_active: true,
        is_admin
      };

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      setToken(access_token);
      setUser(userData);
    } catch (error: any) {
      // Extract the actual error message properly
      let errorMessage = 'Login failed';

      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          // Handle array of validation errors
          errorMessage = error.response.data.detail
            .map((err: any) => `${err.loc.join('.')}: ${err.msg}`)
            .join(', ');
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else {
          errorMessage = JSON.stringify(error.response.data.detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      throw new Error(errorMessage);
    }
  };

  const register = async (email: string, password: string, is_admin: boolean = false) => {
    try {
      console.log('Attempting registration with:', { email, password, is_admin });

      const response = await authAPI.register(email, password, is_admin);
      console.log('Registration successful:', response.data);

      const { access_token, user_id } = response.data;

      const userData: User = {
        id: user_id,
        email,
        is_active: true,
        is_admin
      };

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      setToken(access_token);
      setUser(userData);
    } catch (error: any) {
      console.log('Full registration error:', error);
      console.log('Error response:', error.response);
      console.log('Error data:', error.response?.data);
      console.log('Error status:', error.response?.status);

      // Extract the actual error message properly
      let errorMessage = 'Registration failed';

      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          // Handle array of validation errors
          errorMessage = error.response.data.detail
            .map((err: any) => {
              if (err.loc && err.msg) {
                return `${err.loc.join('.')}: ${err.msg}`;
              }
              return JSON.stringify(err);
            })
            .join(', ');
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else {
          errorMessage = JSON.stringify(error.response.data.detail);
        }
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }

      console.log('Final registration error message:', errorMessage);
      throw new Error(errorMessage);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setToken(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}