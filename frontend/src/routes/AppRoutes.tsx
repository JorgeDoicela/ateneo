import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from '../modules/auth/components/ProtectedRoute';
import AppLayout from '../core/layouts/AppLayout';
import { Activity } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

// Carga perezosa (Code-Splitting) por módulo de dominio
const CaseList = lazy(() => import('../modules/cases/pages/CaseList'));
const CaseSolve = lazy(() => import('../modules/evaluation/pages/CaseSolve'));
const AteneoRoom = lazy(() => import('../modules/collaboration/pages/AteneoRoom'));
const Login = lazy(() => import('../modules/auth/pages/Login'));
const Register = lazy(() => import('../modules/auth/pages/Register'));
const MagicLogin = lazy(() => import('../modules/auth/pages/MagicLogin'));
const AdminLayout = lazy(() => import('../modules/admin/pages/AdminLayout'));
const AdminUsersPage = lazy(() => import('../modules/admin/pages/AdminUsersPage'));
const AdminMagicLinksPage = lazy(() => import('../modules/admin/pages/AdminMagicLinksPage'));
const TeacherLayout = lazy(() => import('../modules/teacher/pages/TeacherLayout'));
const TeacherCasesPage = lazy(() => import('../modules/teacher/pages/TeacherCasesPage'));
const TeacherAnalyticsPage = lazy(() => import('../modules/teacher/pages/TeacherAnalyticsPage'));
const ScientificBenchmarkView = lazy(() => import('../modules/analytics/components/ScientificBenchmarkView'));
const StudentAnalyticsPage = lazy(() => import('../modules/analytics/pages/StudentAnalyticsPage'));

function RouteLoader() {
  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-3">
      <Activity className="w-8 h-8 text-[#0b57d0] animate-spin" />
      <p className="text-xs text-[#747775]">Cargando módulo clínico...</p>
    </div>
  );
}

/**
 * RootRoleRedirect — Despachador de la ruta raíz '/' según el rol de la sesión
 * - Docente: Redirige automáticamente a su panel de gestión (/teacher/cases)
 * - Administrador: Redirige a la consola de usuarios (/admin/users)
 * - Alumno: Carga el catálogo de simulación formativa (CaseList)
 */
function RootRoleRedirect() {
  const { user } = useAuth();
  if (user?.rol === 'docente') {
    return <Navigate to="/teacher/cases" replace />;
  }
  if (user?.rol === 'administrador') {
    return <Navigate to="/admin/users" replace />;
  }
  return <Navigate to="/cases" replace />;
}

/**
 * AnalyticsRoleRedirect — Encamina la analítica según el rol
 * - Docente: Redirige a la analítica de cohorte (/teacher/analytics)
 * - Alumno / Otros: Renderiza la analítica individual del estudiante (StudentAnalyticsPage)
 */
function AnalyticsRoleRedirect() {
  const { user } = useAuth();
  if (user?.rol === 'docente') {
    return <Navigate to="/teacher/analytics" replace />;
  }
  return <StudentAnalyticsPage />;
}

export default function AppRoutes() {
  return (
    <AppLayout>
      <Suspense fallback={<RouteLoader />}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/auth/magic-login" element={<MagicLogin />} />
          <Route path="/magic-login" element={<Navigate to="/auth/magic-login" replace />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <RootRoleRedirect />
              </ProtectedRoute>
            }
          />

          <Route
            path="/cases"
            element={
              <ProtectedRoute>
                <CaseList />
              </ProtectedRoute>
            }
          />

          <Route
            path="/cases/:id"
            element={
              <ProtectedRoute>
                <CaseSolve />
              </ProtectedRoute>
            }
          />

          <Route
            path="/ateneo"
            element={
              <ProtectedRoute>
                <Navigate to="/teacher/cases" replace />
              </ProtectedRoute>
            }
          />

          <Route
            path="/ateneo/:roomCode"
            element={
              <ProtectedRoute>
                <AteneoRoom />
              </ProtectedRoute>
            }
          />

          <Route
            path="/benchmark"
            element={
              <ProtectedRoute allowedRoles={['administrador']}>
                <ScientificBenchmarkView />
              </ProtectedRoute>
            }
          />

          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <AnalyticsRoleRedirect />
              </ProtectedRoute>
            }
          />

          <Route
            path="/performance"
            element={
              <ProtectedRoute>
                <Navigate to="/analytics" replace />
              </ProtectedRoute>
            }
          />

          <Route
            path="/analytics/benchmark"
            element={
              <ProtectedRoute allowedRoles={['administrador']}>
                <Navigate to="/benchmark" replace />
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['administrador']}>
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/admin/users" replace />} />
            <Route path="users" element={<AdminUsersPage />} />
            <Route path="magic-links" element={<AdminMagicLinksPage />} />
          </Route>

          <Route
            path="/teacher"
            element={
              <ProtectedRoute allowedRoles={['docente', 'administrador']}>
                <TeacherLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/teacher/cases" replace />} />
            <Route path="cases" element={<TeacherCasesPage />} />
            <Route path="analytics" element={<TeacherAnalyticsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </AppLayout>
  );
}
