import Navbar from "@/components/ui/Navbar"
import Sidebar from "@/components/ui/Sidebar"

export default function DashboardLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 shrink-0">
        <Sidebar />
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
