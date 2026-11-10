import { ReactNode } from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from './Navbar';

export interface AppLayoutProps {
  children: ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const location = useLocation();
  const isAuthRoute = ['/login', '/register', '/auth/magic-login', '/magic-login'].some(p =>
    location.pathname.startsWith(p)
  );

  if (isAuthRoute) {
    return (
      <div className="min-h-screen bg-[#f0f4f9] flex flex-col justify-center items-center font-sans selection:bg-blue-100 selection:text-blue-900 p-4 sm:p-6">
        <main className="w-full flex items-center justify-center">
          {children}
        </main>
      </div>
    );
  }

  // Rutas espaciales/inmersivas (Simulador Hospitalario 3D): Vista Edge-to-Edge sin márgenes restrictivos ni scrollbar
  const isImmersiveRoute = ['/hospital-3d'].some(p =>
    location.pathname.startsWith(p)
  );

  if (isImmersiveRoute) {
    return (
      <div className="h-screen w-screen bg-[#f0f4f9] flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900 overflow-hidden">
        <Navbar />
        <main className="w-full h-[calc(100vh-4rem)] flex-1 relative z-10 overflow-hidden p-0 m-0">
          {children}
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f0f4f9] flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900 relative overflow-x-clip">
      {/* Halos de Luz Ambiental (Aurora de IA Ateneo+: Cyan, Azul, Violeta) para refracción Glassmorphism */}
      <div 
        className="pointer-events-none fixed -top-32 -left-32 w-[28rem] h-[28rem] bg-gradient-to-br from-cyan-400/20 via-blue-500/15 to-transparent rounded-full blur-3xl"
        aria-hidden="true"
      />
      <div 
        className="pointer-events-none fixed top-1/4 -right-32 w-[32rem] h-[32rem] bg-gradient-to-tl from-violet-500/15 via-indigo-500/12 to-transparent rounded-full blur-3xl"
        aria-hidden="true"
      />
      <div 
        className="pointer-events-none fixed bottom-10 left-1/3 w-[26rem] h-[26rem] bg-gradient-to-tr from-cyan-400/10 via-blue-500/10 to-transparent rounded-full blur-3xl"
        aria-hidden="true"
      />

      <Navbar />

      <main className="w-full max-w-[1680px] mx-auto px-4 sm:px-8 lg:px-12 py-8 flex-1 relative z-10">
        {children}
      </main>

      <footer className="bg-white/80 backdrop-blur-md border-t border-slate-200/60 py-4 text-xs text-slate-500 relative z-10">
        <div className="w-full max-w-[1680px] mx-auto px-4 sm:px-8 flex flex-col sm:flex-row items-center justify-between gap-2.5 text-center sm:text-left">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-800">ATENEO+</span>
            <span className="text-slate-300">•</span>
            <span className="text-[11px] text-slate-500">Prototipo experimental en desarrollo activo</span>
            <span className="text-slate-300 hidden md:inline">•</span>
            <span className="text-[11px] text-slate-400 hidden md:inline">GPC Ecuador</span>
          </div>

          <p className="text-[11px] text-slate-400">
            Uso formativo de simulación • No apto para pacientes reales
          </p>
        </div>
      </footer>
    </div>
  );
}
