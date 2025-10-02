export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_admin: boolean;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  status: "todo" | "in_progress" | "done";
  created_at: string;
  owner_id: number;
  owner: User;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  is_admin: boolean;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    is_admin?: boolean
  ) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}
