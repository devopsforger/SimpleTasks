import type {NextConfig} from "next";

const nextConfig: NextConfig = {
  // Enable static exports for production build
  output: process.env.NODE_ENV === "production" ? "export" : undefined,
  trailingSlash: true,
  images: {
    unoptimized: true, // Required for static export
  },
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
  // Disable TypeScript errors during build
  typescript: {
    ignoreBuildErrors: process.env.NODE_ENV === "production",
  },
  // Disable ESLint during build
  eslint: {
    ignoreDuringBuilds: process.env.NODE_ENV === "production",
  },
};

export default nextConfig;
