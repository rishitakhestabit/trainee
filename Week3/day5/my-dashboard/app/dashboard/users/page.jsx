"use client"

import { useMemo, useState } from "react"
import Input from "@/components/ui/Input"
import Badge from "@/components/ui/Badge"

const USERS = [
  { name: "Harsh Jindal", email: "uharsh.jindal@example.com", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Niharika Singh", email: "niharika42@example.com", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Anurag Sharma", email: "anurag@example.net", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Shubham Tiwary", email: "shubhamk@example.org", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
  { name: "Ruchira KUmar", email: "ruchira.kumar@example.org", role: "User", createdAt: "18/10/2024 05:27", updatedAt: "18/10/2024 05:27" },
]

export default function UsersPage() {
  const [q, setQ] = useState("")

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase()
    if (!query) return USERS
    return USERS.filter((u) =>
      [u.name, u.email, u.role].some((v) => v.toLowerCase().includes(query))
    )
  }, [q])

  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm text-gray-500">Users / List</div>
        <h1 className="text-3xl font-bold text-gray-900 mt-1">Users</h1>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="text-sm text-gray-600">
            Showing <span className="font-semibold">{filtered.length}</span> results
          </div>

          <div className="w-full sm:w-72">
            <Input
              placeholder="Search"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Name</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Email</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Role</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Created at</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Updated at</th>
              </tr>
            </thead>

            <tbody className="divide-y">
              {filtered.map((u, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition">
                  <td className="px-4 py-3 text-sm text-gray-900">{u.name}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{u.email}</td>
                  <td className="px-4 py-3 text-sm">
                    <Badge variant="success">{u.role}</Badge>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{u.createdAt}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{u.updatedAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* simple footer like reference */}
        <div className="p-4 border-t text-sm text-gray-600 flex items-center justify-between">
          <span>Showing 1 to {filtered.length} of {filtered.length} results</span>
          <div className="flex gap-2">
            <button className="px-3 py-1 rounded border hover:bg-gray-50">1</button>
            <button className="px-3 py-1 rounded border hover:bg-gray-50">2</button>
          </div>
        </div>
      </div>
    </div>
  )
}
