'use client'

import { useState } from 'react'
import WelcomeModal from '@/components/ui/WelcomeModal'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Input from '@/components/ui/Input'


export default function Home() {
  const [showWelcome, setShowWelcome] = useState(false)
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-1">Dashboard</h1>
          <nav className="text-sm">
            <span className="text-gray-400">Dashboard</span>
          </nav>
        </div>
        
        {/* Button to open Welcome Modal */}
        <Button 
          variant="wine" 
          size="md"
          onClick={() => setShowWelcome(true)}
        >
          HI,CLICK ME!
        </Button>
      </div>

      {/* Colored Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Primary Card" variant="primary">
          <p className="text-gray-600 mb-4">Some quick example text to build on the card title.</p>
          <Button variant="primary" size="sm">View Details</Button>
        </Card>

        <Card title="Warning Card" variant="warning">
          <p className="text-gray-600 mb-4">Some quick example text to build on the card title.</p>
          <Button variant="warning" size="sm">View Details</Button>
        </Card>

        <Card title="Success Card" variant="success">
          <p className="text-gray-600 mb-4">Some quick example text to build on the card title.</p>
          <Button variant="success" size="sm">View Details</Button>
        </Card>

        <Card title="Danger Card" variant="danger">
          <p className="text-gray-600 mb-4">Some quick example text to build on the card title.</p>
          <Button variant="danger" size="sm">View Details</Button>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Area Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            Area Chart Example
          </h3>
          <div className="h-64 bg-gradient-to-b from-blue-100 to-blue-50 rounded flex items-center justify-center border border-blue-200">
            <p className="text-gray-500">Chart visualization area</p>
          </div>
        </div>

        {/* Bar Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Bar Chart Example
          </h3>
          <div className="h-64 bg-gradient-to-b from-blue-100 to-blue-50 rounded flex items-center justify-center border border-blue-200">
            <p className="text-gray-500">Chart visualization area</p>
          </div>
        </div>
      </div>

      {/* DataTable */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="font-semibold text-gray-800 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            DataTable Example
          </h3>
        </div>
        
        <div className="px-6 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Show</span>
              <select className="border border-gray-300 rounded px-3 py-1 text-sm">
                <option>10</option>
                <option>25</option>
                <option>50</option>
                <option>100</option>
              </select>
              <span className="text-sm text-gray-600">entries</span>
            </div>
            
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <label className="text-sm text-gray-600">Search:</label>
              <Input 
                type="search" 
                placeholder="Search..."
                className="w-full sm:w-64"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Name</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Position</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Office</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Age</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                <tr className="hover:bg-gray-50 transition">
                  <td className="px-4 py-3 text-sm text-gray-800">Rishita Kumar</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Technical Trainee</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Mumbai</td>
                  <td className="px-4 py-3 text-sm text-gray-600">22</td>
                  <td className="px-4 py-3"><Badge variant="success">Active</Badge></td>
                </tr>
                <tr className="hover:bg-gray-50 transition">
                  <td className="px-4 py-3 text-sm text-gray-800">Harshit Sharma</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Accountant</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Delhi</td>
                  <td className="px-4 py-3 text-sm text-gray-600">63</td>
                  <td className="px-4 py-3"><Badge variant="warning">Pending</Badge></td>
                </tr>
                <tr className="hover:bg-gray-50 transition">
                  <td className="px-4 py-3 text-sm text-gray-800">Niharika Singh</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Junior Technical Author</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Noida</td>
                  <td className="px-4 py-3 text-sm text-gray-600">23</td>
                  <td className="px-4 py-3"><Badge variant="success">Active</Badge></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <WelcomeModal 
        isOpen={showWelcome}
        onClose={() => setShowWelcome(false)}
      />
    </div>
  )
}