import { BrowserRouter as Router } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-background">
          <div className="container mx-auto py-8">
            <h1 className="text-4xl font-bold text-center mb-4">
              🚗 AutoSense AI Platform
            </h1>
            <p className="text-center text-muted-foreground mb-8">
              AI-powered predictive maintenance for vehicles
            </p>
            <div className="bg-card rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
              <h2 className="text-2xl font-semibold mb-4">✅ Project Setup Complete!</h2>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">📁</span>
                  <span>Backend structure created</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl">⚛️</span>
                  <span>Frontend structure created</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🤖</span>
                  <span>ML pipeline scaffolding ready</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl">📊</span>
                  <span>Database schema pending</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🔐</span>
                  <span>Authentication pending</span>
                </div>
              </div>
              <div className="mt-6 pt-6 border-t">
                <p className="text-sm text-muted-foreground">
                  Next: Install dependencies and implement database models
                </p>
              </div>
            </div>
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App
