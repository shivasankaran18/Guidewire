import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Onboarding from './pages/Onboarding'
import WorkerDashboard from './pages/WorkerDashboard'
import WorkerAssistant from './pages/WorkerAssistant'
import PolicyPage from './pages/PolicyPage'
import ClaimsPage from './pages/ClaimsPage'
import ClaimDetailPage from './pages/ClaimDetailPage'
import AppealPage from './pages/AppealPage'
import AdminDashboard from './pages/AdminDashboard'
import Navbar from './components/shared/Navbar'
import ErrorBoundary from './components/shared/ErrorBoundary'
import LoadingSpinner from './components/shared/LoadingSpinner'

function ProtectedRoute({ children, requiredRole }) {
  const { user, isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0f172a] flex items-center justify-center">
        <LoadingSpinner text="Loading..." />
      </div>
    )
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (requiredRole && user?.role !== requiredRole && user?.role !== 'SUPER_ADMIN') {
    return <Navigate to="/dashboard" replace />
  }
  return children
}

export default function App() {
  const { isAuthenticated, user, loading } = useAuth()

  if (loading) {
    return (
      <ErrorBoundary>
        <div className="min-h-screen bg-[#0f172a] flex items-center justify-center">
          <LoadingSpinner text="Initializing..." />
        </div>
      </ErrorBoundary>
    )
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-[#0f172a]">
        {isAuthenticated && <Navbar />}
        <Routes>
          <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <WorkerDashboard />
            </ProtectedRoute>
          } />
          <Route path="/assistant" element={
            <ProtectedRoute>
              <WorkerAssistant />
            </ProtectedRoute>
          } />
          <Route path="/policy" element={
            <ProtectedRoute>
              <PolicyPage />
            </ProtectedRoute>
          } />
          <Route path="/claims" element={
            <ProtectedRoute>
              <ClaimsPage />
            </ProtectedRoute>
          } />
          <Route path="/claims/:claimId" element={
            <ProtectedRoute>
              <ClaimDetailPage />
            </ProtectedRoute>
          } />
          <Route path="/appeal/:claimId" element={
            <ProtectedRoute>
              <AppealPage />
            </ProtectedRoute>
          } />
          <Route path="/admin" element={
            <ProtectedRoute requiredRole="ADMIN">
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </ErrorBoundary>
  )
}
