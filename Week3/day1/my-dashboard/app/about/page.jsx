
'use client'

import { useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Input from '@/components/ui/Input'
import WelcomeModal from '@/components/ui/WelcomeModal'




export default function AboutPage() {
const [showWelcome, setShowWelcome] = useState(false)
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">About Us</h1>
        <nav className="text-sm">
          <span className="text-gray-400">About</span>
        </nav>
      </div>

      {/* Content */}
      <div className="bg-white shadow p-8">
        <h2 className="text-2xl font-semibold mb-4" style={{ color: '#4A0E2B' }}>
          Welcome to ZUDEE Platform
        </h2>
        
        <div className="space-y-4 text-gray-600">
          <p>
            ZUDEE is a comprehensive dashboard solution designed to help you manage your 
            business operations efficiently. Our platform provides powerful tools for 
            data visualization, analytics, and team collaboration.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            {/* Mission Card */}
            <div className="p-6 rounded-lg" style={{ backgroundColor: '#F5E6ED' }}>
              <h3 className="text-lg font-semibold mb-3" style={{ color: '#4A0E2B' }}>
                Our Mission
              </h3>
              <p className="text-gray-700">
                To empower businesses with intuitive tools that transform complex data 
                into actionable insights.
              </p>
            </div>

            {/* Vision Card */}
            <div className="p-6 rounded-lg" style={{ backgroundColor: '#F5E6ED' }}>
              <h3 className="text-lg font-semibold mb-3" style={{ color: '#4A0E2B' }}>
                Our Vision
              </h3>
              <p className="text-gray-700">
                To become the leading platform for business intelligence and data 
                management worldwide.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}


