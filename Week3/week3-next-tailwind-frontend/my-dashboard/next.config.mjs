/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "assets.startbootstrap.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "img.freepik.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "www.gravitykit.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "demos.themeselection.com",
        pathname: "/**",
      },
    ],
  },
}

export default nextConfig
