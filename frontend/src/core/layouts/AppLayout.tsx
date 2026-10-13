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
    <div className="min-h-screen bg-[#f0f4f9] flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900">
      <Navbar />

      <main className="w-full max-w-[1680px] mx-auto px-4 sm:px-8 lg:px-12 py-8 flex-1">
        {children}
      </main>

      <footer className="bg-white border-t border-slate-200/80 py-6 text-center text-xs text-[#747775]">
        <div className="w-full max-w-[1680px] mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <HeartPulse className="w-4 h-4 text-[#0b57d0]" />
            <span>ATENEO+ • Simulador Clínico Basado en RAG Híbrido & Normativa Oficial MSP Ecuador</span>
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <span>GPC Ecuador 2026</span>
            <span>•</span>
            <span>Inteligencia Artificial Clínica</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
