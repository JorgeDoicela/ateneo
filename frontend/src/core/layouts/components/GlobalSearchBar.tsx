import { ChangeEvent } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { Search, SlidersHorizontal, X } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';

/**
 * GlobalSearchBar — Cápsula de búsqueda de cristal líquido desacoplada con sincronización de URL
 */
export default function GlobalSearchBar() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  const isAuthRoute = ['/login', '/register', '/auth/magic-login', '/magic-login'].some(p => 
    location.pathname.startsWith(p)
  );

  // Solo se renderiza para usuarios autenticados fuera del flujo de login
  if (isAuthRoute || !user) {
    return null;
  }

  const searchQuery = searchParams.get('q') || '';

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    if (location.pathname !== '/') {
      navigate(`/?q=${encodeURIComponent(val)}`);
    } else {
      if (val) {
        setSearchParams({ q: val });
      } else {
        setSearchParams({});
      }
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto hidden md:flex items-center">
      <div className="w-full bg-white/70 hover:bg-white/90 backdrop-blur-md focus-within:bg-white focus-within:shadow-md focus-within:shadow-indigo-500/5 focus-within:ring-2 focus-within:ring-blue-500/20 rounded-full px-4 py-2 transition-all flex items-center gap-3 border border-slate-200/60 focus-within:border-blue-400">
        <Search className="w-4 h-4 text-blue-600/70 shrink-0" />
        <input
          type="text"
          placeholder="Buscar en Ateneo: casos clínicos, síntomas, diagnósticos o GPC MSP..."
          value={searchQuery}
          onChange={handleSearchChange}
          className="w-full bg-transparent text-xs sm:text-sm text-[#1f1f1f] focus:outline-none placeholder:text-[#747775]"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchParams({})}
            className="text-xs text-[#747775] hover:text-[#1f1f1f] p-1 rounded-full hover:bg-slate-200/60 transition-colors cursor-pointer"
            title="Limpiar búsqueda"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
        <button
          title="Filtros de Búsqueda"
          onClick={() => navigate('/?filter=open')}
          className="p-1 text-[#747775] hover:text-[#1f1f1f] rounded-full hover:bg-slate-200/60 transition-colors cursor-pointer shrink-0"
        >
          <SlidersHorizontal className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
