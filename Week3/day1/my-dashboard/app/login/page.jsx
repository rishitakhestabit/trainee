import Link from "next/link"
import Button from "@/components/ui/Button"
import Input from "@/components/ui/Input"

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#5B2A42] to-[#8C2F4E] px-4">
      
      {/* Card */}
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-10">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-semibold text-gray-900">
            Login
          </h1>
          <p className="mt-2 text-sm text-gray-500">
            Welcome back — please enter your details
          </p>
        </div>

        {/* Form */}
        <form className="space-y-6">

          <Input 
            type="text" 
            placeholder="Username" 
          />

          <Input 
            type="password" 
            placeholder="Password" 
          />

          {/* Options Row */}
          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 text-gray-600">
              <input
                type="checkbox"
                className="accent-[#8C2F4E]"
              />
              Remember me
            </label>

            <button
              type="button"
              className="text-[#8C2F4E] font-medium hover:underline"
            >
              Forgot password?
            </button>
          </div>

          {/* Login Button */}
          <Button
            variant="wine"
            size="lg"
            className="w-full flex justify-center tracking-wide"
          >
            LOGIN
          </Button>

          {/* Footer Link */}
          <div className="pt-4 text-center">
            <Link
              href="/"
              className="text-sm text-[#8C2F4E] font-medium hover:underline"
            >
              Back to Landing
            </Link>
          </div>

        </form>
      </div>

    </div>
  )
}
