'use client'

export default function Sidebar() {
  const menuItems = [
    { icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6', label: 'Dashboard' },
    { icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', label: 'Layouts', hasDropdown: true },
    { icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', label: 'Pages', hasDropdown: true },
  ];

  const addonItems = [
    { icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', label: 'Charts' },
    { icon: 'M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z', label: 'Tables' },
  ];

  return (
    <aside 
      className="text-white w-56 min-h-screen flex flex-col"
      style={{ backgroundColor: '#4A0E2B' }}
    >
      {/* Core Section */}
      <div className="px-4 py-3">
        <p className="text-xs text-gray-400 uppercase font-semibold mb-2">Core</p>
        <ul className="space-y-1">
          {menuItems.map((item, index) => (
            <li key={index}>
              <a 
                href="#" 
                className={`flex items-center gap-3 px-3 py-2 rounded transition hover:opacity-80 ${index === 0 ? 'text-gray-800' : 'text-white'}`}
                style={{ backgroundColor: index === 0 ? '#E8D5B7' : 'transparent' }}
                onMouseEnter={(e) => {
                  if (index !== 0) e.currentTarget.style.backgroundColor = '#6B1B3D';
                }}
                onMouseLeave={(e) => {
                  if (index !== 0) e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                </svg>
                <span className="text-sm">{item.label}</span>
                {item.hasDropdown && (
                  <svg className="w-4 h-4 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                )}
              </a>
            </li>
          ))}
        </ul>
      </div>

      {/* Addons Section */}
      <div className="px-4 py-3 border-t" style={{ borderColor: '#7A2648' }}>
        <p className="text-xs text-gray-400 uppercase font-semibold mb-2">Addons</p>
        <ul className="space-y-1">
          {addonItems.map((item, index) => (
            <li key={index}>
              <a 
                href="#" 
                className="flex items-center gap-3 px-3 py-2 rounded transition"
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#6B1B3D'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                </svg>
                <span className="text-sm">{item.label}</span>
              </a>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}