export default function AboutPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      {/* Top strip (subtle brand) */}
      <div className="h-2 w-full bg-[#8C2F4E]" />

      <section className="mx-auto max-w-5xl px-4 py-12">
        {/* Header */}
        <div className="text-center">
          <p className="text-xs uppercase tracking-widest text-gray-500">
            About ZUDEE
          </p>

          <h1 className="mt-3 text-4xl font-bold text-gray-900">
            Built for clarity, speed, and clean UI.
          </h1>

          <p className="mt-4 text-base text-gray-600 max-w-2xl mx-auto leading-relaxed">
            ZUDEE is a modern dashboard UI that helps teams visualize analytics, manage
            users, and keep workflows organized, like all with reusable components and a
            responsive layout.
          </p>
        </div>

        {/* Cards */}
        <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
            <p className="text-xs uppercase tracking-wide text-gray-500">
              Our Mission
            </p>
            <h2 className="mt-2 text-lg font-semibold text-gray-900">
              Turn data into decisions
            </h2>
            <p className="mt-3 text-sm text-gray-600 leading-relaxed">
              Empower teams with intuitive UI that makes complex information easy to
              understand and act on.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
            <p className="text-xs uppercase tracking-wide text-gray-500">
              Our Vision
            </p>
            <h2 className="mt-2 text-lg font-semibold text-gray-900">
              A smarter workspace for everyone
            </h2>
            <p className="mt-3 text-sm text-gray-600 leading-relaxed">
              Create a clean, fast, and consistent experience for dashboards, on any
              screen size.
            </p>
          </div>
        </div>

        {/* Highlight */}
        <div className="mt-8 bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-900">
            What we focus on
          </h3>

          <ul className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm text-gray-600">
            <li className="rounded-lg bg-gray-50 border border-gray-200 px-4 py-3">
              Reusable components
            </li>
            <li className="rounded-lg bg-gray-50 border border-gray-200 px-4 py-3">
              Responsive layouts
            </li>
            <li className="rounded-lg bg-gray-50 border border-gray-200 px-4 py-3">
              Clean routing structure
            </li>
          </ul>

        </div>
      </section>
    </main>
  )
}
