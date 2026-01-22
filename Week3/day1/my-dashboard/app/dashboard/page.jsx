import Link from 'next/link'
import Button from '@/components/ui/Button'

export default function Home() {
  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="text-center space-y-8 max-w-2xl px-4">
  
        <h1 className="text-5xl font-bold text-gray-800">
          Welcome to <span style={{ color: '#4A0E2B' }}>ZUDEE</span>
        </h1>


        <p className="text-xl text-gray-600">
          Your all-in-one platform for business intelligence, data visualization, 
          and team collaboration. Get started today and transform how you work.
        </p>


        <div className="gap-4 justify-center items-center mt-8">
          <Link href="/">
            <Button variant="wine" size="lg">
              Go to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}



