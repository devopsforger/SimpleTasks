import type {NextConfig} from "next";

const nextConfig: NextConfig = {
  typedRoutes: true,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
  // Enable Turbopack for faster development
  // Use: next dev --turbo :cite[1]:cite[2]
};

export default nextConfig;
