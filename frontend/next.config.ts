import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  images: {
    formats: ["image/avif", "image/webp"],
  },
  webpack: (config, { dev }) => {
    if (dev) {
      // Avoid corrupted .next/cache chunks when dev and build overlap on Windows.
      config.cache = { type: "memory" };
    }
    return config;
  },
};

export default nextConfig;
