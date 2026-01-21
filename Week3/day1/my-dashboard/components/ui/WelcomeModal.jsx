'use client'

import Modal from './Modal'
import Button from './Button'

export default function WelcomeModal({ isOpen, onClose }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      {/* Illustration/Icon */}
      <div className="mb-6">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-4" style={{ backgroundColor: '#4A0E2B' }}>
          <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        
        {/* Celebration Banner */}
        <div className="flex items-center justify-center gap-2 mb-4">
          <span className="text-2xl">🎉</span>
          <span className="text-lg font-bold" style={{ color: '#4A0E2B' }}>HEY GANG</span>
          <span className="text-2xl">🎉</span>
        </div>
      </div>

      {/* Title */}
      <h2 className="text-2xl font-bold text-gray-800 mb-4">
        Welcome to ZUDEE Corporation!
      </h2>

      {/* Description */}
      <p className="text-gray-600 mb-6 leading-relaxed">
        The ZUDEE platform is your go-to all-in-one solution to onboard, 
        pay and insure your employees.
      </p>

      <p className="text-gray-600 mb-8">
        Let's get started by learning a little bit more about your organization.
      </p>

      {/* Action Button */}
      <Button 
        variant="danger" 
        size="md"
        onClick={onClose}
      >
        Set Up My Company
      </Button>
    </Modal>
  )
}