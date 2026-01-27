"use client"

import { useState } from "react"

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts"

import Card from "@/components/ui/Card"
import Button from "@/components/ui/Button"
import Badge from "@/components/ui/Badge"
import Input from "@/components/ui/Input"
import WelcomeModal from "@/components/ui/WelcomeModal"

/* ------------------ DUMMY DATA ------------------ */

const revenueData = [
  { name: "Mon", revenue: 1200 },
  { name: "Tue", revenue: 2100 },
  { name: "Wed", revenue: 1800 },
  { name: "Thu", revenue: 2600 },
  { name: "Fri", revenue: 2400 },
  { name: "Sat", revenue: 3200 },
  { name: "Sun", revenue: 2800 },
]

const signupData = [
  { name: "Mon", users: 35 },
  { name: "Tue", users: 55 },
  { name: "Wed", users: 48 },
  { name: "Thu", users: 62 },
  { name: "Fri", users: 58 },
  { name: "Sat", users: 75 },
  { name: "Sun", users: 69 },
]

/* ------------------ PAGE ------------------ */

export default function DashboardHome() {
  const [showWelcome, setShowWelcome] = useState(false)

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500">Dashboard</p>
        </div>

        <Button variant="wine" size="md" onClick={() => setShowWelcome(true)}>
          HI, CLICK ME!
        </Button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

        <Card title="Primary Card" variant="primary">
          <p className="text-gray-600 mb-4">
            Some quick example text to build on the card title.
          </p>
          <Button variant="primary" size="sm">View Details</Button>
        </Card>

        <Card title="Warning Card" variant="warning">
          <p className="text-gray-600 mb-4">
            Some quick example text to build on the card title.
          </p>
          <Button variant="warning" size="sm">View Details</Button>
        </Card>

        <Card title="Success Card" variant="success">
          <p className="text-gray-600 mb-4">
            Some quick example text to build on the card title.
          </p>
          <Button variant="success" size="sm">View Details</Button>
        </Card>

        <Card title="Danger Card" variant="danger">
          <p className="text-gray-600 mb-4">
            Some quick example text to build on the card title.
          </p>
          <Button variant="danger" size="sm">View Details</Button>
        </Card>

      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Area */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-4">Revenue (Area)</h3>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#8C2F4E"
                  fill="#8C2F4E"
                  fillOpacity={0.25}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-4">Signups (Bar)</h3>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={signupData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar
                  dataKey="users"
                  fill="#5B2A42"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow">

        <div className="px-6 py-4 border-b">
          <h3 className="font-semibold">DataTable Example</h3>
        </div>

        <div className="px-6 py-4">

          <div className="flex flex-col sm:flex-row justify-between gap-4 mb-4">

            <div className="flex items-center gap-2">
              <span className="text-sm">Show</span>
              <select className="border rounded px-2 py-1">
                <option>10</option>
                <option>25</option>
                <option>50</option>
              </select>
              <span className="text-sm">entries</span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm">Search:</span>
              <Input placeholder="Search..." className="w-64" />
            </div>

          </div>

          <div className="overflow-x-auto">

            <table className="w-full">

              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-2 text-left">Name</th>
                  <th className="px-4 py-2 text-left">Position</th>
                  <th className="px-4 py-2 text-left">Office</th>
                  <th className="px-4 py-2 text-left">Age</th>
                  <th className="px-4 py-2 text-left">Status</th>
                </tr>
              </thead>

              <tbody className="divide-y">

                <tr>
                  <td className="px-4 py-2">Rishita Kumar</td>
                  <td className="px-4 py-2">Technical Trainee</td>
                  <td className="px-4 py-2">Mumbai</td>
                  <td className="px-4 py-2">22</td>
                  <td className="px-4 py-2">
                    <Badge variant="success">Active</Badge>
                  </td>
                </tr>

                <tr>
                  <td className="px-4 py-2">Harshit Sharma</td>
                  <td className="px-4 py-2">Accountant</td>
                  <td className="px-4 py-2">Delhi</td>
                  <td className="px-4 py-2">63</td>
                  <td className="px-4 py-2">
                    <Badge variant="warning">Pending</Badge>
                  </td>
                </tr>

                <tr>
                  <td className="px-4 py-2">Niharika Singh</td>
                  <td className="px-4 py-2">Junior Technical Author</td>
                  <td className="px-4 py-2">Noida</td>
                  <td className="px-4 py-2">23</td>
                  <td className="px-4 py-2">
                    <Badge variant="success">Active</Badge>
                  </td>
                </tr>

              </tbody>

            </table>

          </div>

        </div>
      </div>

      {/* Modal */}
      <WelcomeModal
        isOpen={showWelcome}
        onClose={() => setShowWelcome(false)}
      />

    </div>
  )
}
