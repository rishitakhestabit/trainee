'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Sidebar() {
  const pathname = usePathname()

  const menuItems = [
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Users', href: '/dashboard/users' },     
    { label: 'Profile', href: '/dashboard/profile' },
    { label: 'About', href: '/about' },
  ]

  const addonItems = [
    { id: 'charts', label: 'Charts', href: '/dashboard/charts' },
    { id: 'tables', label: 'Tables', href: '/dashboard/tables' },
  ]

  const authItems = [
    { label: 'Login', href: '/login' },               
  ]

  const isActive = (href) => pathname === href

  return (
    <aside
      className="w-56 min-h-screen flex flex-col text-white"
      style={{ backgroundColor: '#5A1E3A' }}
    >
      {/* CORE */}
      <div className="px-4 py-4">
        <p className="text-xs uppercase font-semibold mb-2 text-[#C8A882]">
          Core
        </p>

        <ul className="space-y-1">
          {menuItems.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`block px-3 py-2 rounded text-sm transition ${
                  isActive(item.href)
                    ? 'bg-[#E8D5B7] text-gray-800'
                    : 'hover:bg-[#6B1B3D]'
                }`}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>

      {/* ADDONS */}
      <div
        className="px-4 py-4 border-t"
        style={{ borderColor: '#7A2648' }}
      >
        <p className="text-xs uppercase font-semibold mb-2 text-[#C8A882]">
          Addons
        </p>

        <ul className="space-y-1">
          {addonItems.map((item) => (
            <li key={item.id}>
              <Link
                href={item.href}
                className="block px-3 py-2 rounded text-sm transition hover:bg-[#6B1B3D]"
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>

      {/* AUTH */}
      <div
        className="px-4 py-4 border-t mt-auto"
        style={{ borderColor: '#7A2648' }}
      >
        <p className="text-xs uppercase font-semibold mb-2 text-[#C8A882]">
          Auth
        </p>

        <ul className="space-y-1">
          {authItems.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`block px-3 py-2 rounded text-sm transition ${
                  isActive(item.href)
                    ? 'bg-[#E8D5B7] text-gray-800'
                    : 'hover:bg-[#6B1B3D]'
                }`}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  )
}
