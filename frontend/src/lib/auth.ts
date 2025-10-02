import {jwtDecode} from "jwt-decode";

interface JwtPayload {
  sub: string;
  exp: number;
}

export const isTokenExpired = (token: string): boolean => {
  try {
    const decoded: JwtPayload = jwtDecode(token);
    return decoded.exp * 1000 < Date.now();
  } catch {
    return true;
  }
};

export const getStoredAuth = () => {
  if (typeof window === "undefined") return null;

  const token = localStorage.getItem("token");
  const userStr = localStorage.getItem("user");

  if (!token || !userStr) return null;

  if (isTokenExpired(token)) {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    return null;
  }

  try {
    const user = JSON.parse(userStr);
    return {token, user};
  } catch {
    return null;
  }
};
