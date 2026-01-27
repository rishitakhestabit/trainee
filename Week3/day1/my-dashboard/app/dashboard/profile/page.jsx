import Image from "next/image"
import Link from "next/link"
import Button from "@/components/ui/Button"

export default function ProfilePage() {
  return (
    <div className="space-y-6">

      {/* Back */}
      <Link
        href="/dashboard"
        className="text-sm text-[#8C2F4E] hover:underline"
      >
        ← Go back
      </Link>

      {/* Card */}
      <div className="bg-white rounded-lg shadow p-6">

        {/* Top */}
        <div className="flex flex-col md:flex-row gap-6 items-center md:items-start">

          {/* Photo */}
          <div className="relative w-28 h-28 rounded-lg overflow-hidden border">
            <Image
              src="/pic.jpeg"
              alt="Profile"
              fill
              className="object-cover"
            />
          </div>

          {/* Basic Info */}
          <div className="flex-1 space-y-3 text-center md:text-left">
            <h1 className="text-2xl font-semibold text-gray-900">
              Rishita Kumar
            </h1>

            <p className="text-gray-600">
              Engineer
            </p>

            <p className="text-sm text-[#8C2F4E]">
              rk@example.com
            </p>
          </div>

        </div>

        {/* Divider */}
        <div className="my-6 border-t" />

        {/* Bio */}
        <div>
          <h2 className="text-sm font-semibold text-gray-900 mb-2">
            Bio
          </h2>

          <p className="text-sm text-gray-600 leading-relaxed">
            HI, I AM RISHITA KUMAR
          </p>
        </div>

        {/* Action */}
        <div className="mt-6">
          <Button variant="wine" size="sm">
            Edit Profile
          </Button>
        </div>

      </div>
    </div>
  )
}
