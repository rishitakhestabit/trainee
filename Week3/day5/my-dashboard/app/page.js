"use client"

import { motion } from "framer-motion"
import Image from "next/image"
import Link from "next/link"

export default function LandingPage() {
  return (
    <div className="bg-white text-gray-800">

      {/* HERO */}
      <section className="bg-gradient-to-br from-[#5B2A42] to-[#8C2F4E] text-white">
        <div className="max-w-7xl mx-auto px-6 py-24 grid md:grid-cols-2 gap-12 items-center">

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6">
              A Powerful Dashboard For Modern Businesses
            </h1>

            <p className="text-lg text-gray-200 mb-8">
              Track analytics, manage users, monitor performance, and grow your
              business, all in one elegant platform.
            </p>

            <Link href="/dashboard">
              <button className="bg-white text-[#8C2F4E] px-6 py-3 rounded-lg font-semibold shadow-lg
              hover:scale-105 hover:shadow-xl transition-all duration-300">
                Enter Dashboard
              </button>
            </Link>
          </motion.div>

          {/* IMAGE */}
          <div className="relative w-full h-80 md:h-[400px] hover:scale-105 transition-transform duration-500">
            <Image
              src="/dashboard-preview.png"
              alt="Dashboard Preview"
              fill
              className="object-contain drop-shadow-2xl"
            />
          </div>

        </div>
      </section>

      {/* FEATURES */}
      <section className="py-20 bg-gray-50">
        <div className="text-center mb-14 px-6">
          <h2 className="text-3xl font-bold mb-3">Everything You Need</h2>
          <p className="text-gray-600">
            Built for teams who want speed, clarity, and performance.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto px-6">
          {[
            { title: "Analytics", desc: "Real-time insights and tracking." },
            { title: "User Control", desc: "Role-based access management." },
            { title: "Smart Reports", desc: "Export reports instantly." },
          ].map((item, i) => (
            <div
              key={i}
              className="bg-white p-8 rounded-xl shadow hover:shadow-xl
              hover:-translate-y-2 transition-all duration-300"
            >
              <h3 className="text-xl font-semibold mb-3 text-[#8C2F4E]">
                {item.title}
              </h3>
              <p className="text-gray-600">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="py-20">
        <div className="text-center mb-14 px-6">
          <h2 className="text-3xl font-bold">Trusted by Growing Teams</h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto px-6">
          {[
            {
              name: "Rishita Kumar",
              text: "This dashboard helped our team track everything in one place.",
            },
            {
              name: "Harshit Sharma",
              text: "Clean design and powerful features.",
            },
            {
              name: "Niharika Singh",
              text: "Analytics tools saved us hours of work.",
            },
          ].map((item, i) => (
            <div
              key={i}
              className="bg-white p-8 rounded-xl shadow border
              hover:scale-105 transition-transform duration-300"
            >
              <p className="text-gray-600 mb-4">“{item.text}”</p>
              <h4 className="font-semibold text-[#8C2F4E]">{item.name}</h4>
            </div>
          ))}
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-[#5B2A42] text-gray-200 py-10">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h3 className="text-xl font-semibold mb-2">Zudee Dashboard</h3>
          <p className="text-gray-400 text-sm">
            © {new Date().getFullYear()} Zudee. All rights reserved.
          </p>
        </div>
      </footer>

    </div>
  )
}
