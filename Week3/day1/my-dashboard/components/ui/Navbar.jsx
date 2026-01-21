export default function Navbar() {
  return (
    <nav 
      className="text-white px-4 py-3 flex items-center justify-between sticky top-0 z-50"
      style={{ backgroundColor: '#D4A574' }}
    >
      {/* Left: Brand + Hamburger */}
      <div className="flex items-center gap-3">
        <button className="lg:hidden text-white">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <span className="text-xl font-semibold">ZUDEE</span>
      </div>

      {/* Right: Search + User */}
      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="hidden md:flex items-center rounded px-3 py-2" style={{ backgroundColor: '#eeecd9' }}>
          <input 
            type="text" 
            placeholder="Search for..." 
            className="bg-transparent border-none outline-none text-sm text-white placeholder-gray-400 w-48"
          />
          <button className="text-white ml-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
        </div>

        {/* User Icon */}
        <button className="text-white">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </button>
      </div>
    </nav>
  );
}