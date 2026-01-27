import "./globals.css"

export const metadata = {
  title: "Zudee — Smart Dashboard Platform",
  description:
    "Modern SaaS dashboard with analytics, reports, and user management built using Next.js & Tailwind.",
  keywords: ["SaaS", "Dashboard", "Next.js", "Admin UI"],
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900 antialiased">
        {children}
      </body>
    </html>
  )
}
