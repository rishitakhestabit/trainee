import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from '@/components/ui/Navbar'
import Sidebar from '@/components/ui/Sidebar'

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: 'Dashboard - Start Bootstrap',
  description: 'Admin Dashboard',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 bg-gray-100 p-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}