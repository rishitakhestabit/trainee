'use client'

import { useState } from 'react'

export default function ProfilePage() {
  const [name, setName] = useState('Rishita Kumar')
  const [email, setEmail] = useState('rishita@zudee.com')

  return (
    <div>
      <h1 className="text-xl font-medium">
        Profile
      </h1>

      <p className="text-sm text-gray-500">
        Edit your basic information
      </p>

      <div className="mt-6 space-y-4">
        <div>
          <label className="block text-sm">
            Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border px-2 py-1 text-sm w-full"
          />
        </div>

        <div>
          <label className="block text-sm">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="border px-2 py-1 text-sm w-full"
          />
        </div>

        <button className="text-sm border px-3 py-1">
          Save
        </button>
      </div>
    </div>
  )
}
