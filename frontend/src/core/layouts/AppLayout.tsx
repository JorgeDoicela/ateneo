import { ReactNode } from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import { HeartPulse } from 'lucide-react';

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

      <footer className="bg-white border-t border-slate-200/80 py-6 text-center text-xs text-[#747775]">
        <div className="w-full max-w-[1680px] mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <HeartPulse className="w-4 h-4 text-[#0b57d0]" />
            <span>ATENEO+ • Simulador Clínico Basado en Guías de Práctica Clínica (GPC Ecuador)</span>
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <span>GPC Ecuador</span>
            <span>•</span>
            <span>Inteligencia Artificial Clínica</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
