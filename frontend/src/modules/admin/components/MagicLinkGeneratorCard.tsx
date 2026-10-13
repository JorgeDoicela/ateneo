import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Link2, 
  Copy, 
  Check, 
  Trash2, 
  Users, 
  AlertCircle,
  Loader2,
  RefreshCw,
  Share2,
  ExternalLink,
  Globe,
  Layers,
  GraduationCap,
  Stethoscope,
  Shield,
  Sparkles,
  CheckCircle2,
  Download,
  Filter,
  UserPlus
} from 'lucide-react';
import authApi from '../../auth/api/authApi';
import type { MagicLinkRecord, MagicLinkCreatePayload, MagicLinkBatchCreatePayload } from '../../../types';
import FloatingLabelInput from '../../../core/ui/FloatingLabelInput';

/**
 * Componente Institucional: Generador y Gestor de Magic Links e Invitaciones Configurables (Ateneo+)
 * Permite a administradores emitir accesos directos nominativos para evaluadores de prueba o cohortes.
 * Soporta multi-ingreso continuo (reutilizable), emisión atómica por lotes con numeración configurable,
 * exportación a CSV, copia estructurada y purga segura de enlaces inactivos.
 * Cumple con el sistema de diseño clínico Ateneo+: Cero emojis, iconos planos sin cajas, Material 3 Canvas (#f0f4f9).
 */
export const MagicLinkGeneratorCard: React.FC = () => {
  // Lista de enlaces y estado de carga
  const [links, setLinks] = useState<MagicLinkRecord[]>([]);
  const [loadingLinks, setLoadingLinks] = useState<boolean>(true);
  const [linksError, setLinksError] = useState<string | null>(null);

  // Parámetros configurables del formulario principal
  const [rol, setRol] = useState<'alumno' | 'docente' | 'administrador'>('alumno');
  const [modo, setModo] = useState<'reutilizable' | 'unico' | 'cohorte'>('reutilizable');
  const [emisionTipo, setEmisionTipo] = useState<'individual' | 'lote'>('individual');
  const [email, setEmail] = useState<string>('');
  const [recipientName, setRecipientName] = useState<string>('Estudiante 1');
  const [duracionHoras, setDuracionHoras] = useState<number>(168); // 7 días por defecto
  const [maxUses, setMaxUses] = useState<number>(100);
  const [targetPath, setTargetPath] = useState<string>('/cases');
  const [cohorteId, setCohorteId] = useState<string>('general');
  const [restrictDomain, setRestrictDomain] = useState<boolean>(false);

  // Parámetros específicos para la emisión en lote
  const [batchPrefix, setBatchPrefix] = useState<string>('Estudiante');
  const [batchStartIndex, setBatchStartIndex] = useState<number>(1);
  const [batchQuantity, setBatchQuantity] = useState<number>(3);

  // Resolución de dominio canónico para enlaces compartidos
  const detectedOrigin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:5174';
  const defaultBaseDomain = detectedOrigin.includes('localhost') 
    ? 'https://ateneo.doicela.dev' 
    : detectedOrigin;
  const [baseDomain, setBaseDomain] = useState<string>(defaultBaseDomain);

  // Estado de envío y enlaces generados recientes
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);
  const [recentGenerated, setRecentGenerated] = useState<MagicLinkRecord[]>([]);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);
  const [copiedAll, setCopiedAll] = useState<boolean>(false);
  const [revokeTargetId, setRevokeTargetId] = useState<string | null>(null);
  const [purgeTargetId, setPurgeTargetId] = useState<string | null>(null);
  const [revoking, setRevoking] = useState<boolean>(false);
  const [purgingRevoked, setPurgingRevoked] = useState<boolean>(false);

  // Filtros de tabla de auditoría
  const [auditFilter, setAuditFilter] = useState<'todos' | 'activos' | 'expirados' | 'revocados'>('todos');

  // Calcular índice correlativo inteligente para sugerir continuación de numeración
  const nextAvailableIndex = useMemo(() => {
    const rolePrefix = rol === 'alumno' ? 'Estudiante' : rol === 'docente' ? 'Docente' : 'Administrador';
    const numbers = links
      .map((l) => {
        const match = l.recipient_name?.match(new RegExp(`^${rolePrefix}\\s*(\\d+)$`, 'i'));
        return match ? parseInt(match[1], 10) : null;
      })
      .filter((n): n is number => n !== null);

    return numbers.length > 0 ? Math.max(...numbers) + 1 : 1;
  }, [links, rol]);

  // Sincronización automática de rol y sugerencia de nombres
  const handleRoleChange = (newRole: 'alumno' | 'docente' | 'administrador') => {
    setRol(newRole);
    if (newRole === 'docente') {
      setTargetPath('/teacher/cases');
      setBatchPrefix('Docente');
      if (recipientName.startsWith('Estudiante') || !recipientName) {
        setRecipientName('Docente 1');
      }
    } else if (newRole === 'administrador') {
      setTargetPath('/admin/users');
      setBatchPrefix('Administrador');
      if (recipientName.startsWith('Estudiante') || recipientName.startsWith('Docente') || !recipientName) {
        setRecipientName('Administrador Evaluador');
      }
    } else {
      setTargetPath('/cases');
      setBatchPrefix('Estudiante');
      if (recipientName.startsWith('Docente') || recipientName.startsWith('Administrador') || !recipientName) {
        setRecipientName('Estudiante 1');
      }
    }
  };

  const fetchLinks = useCallback(async () => {
    setLoadingLinks(true);
    setLinksError(null);
    try {
      const data = await authApi.listMagicLinks();
      setLinks(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al listar enlaces';
      setLinksError(msg);
    } finally {
      setLoadingLinks(false);
    }
  }, []);

  useEffect(() => {
    fetchLinks();
  }, [fetchLinks]);

  // Transformar URL si fue generada con origen local pero se configuró dominio público canónico
  const normalizeShareableUrl = useCallback((rawUrl: string): string => {
    if (!rawUrl) return '';
    try {
      const urlObj = new URL(rawUrl);
      const targetObj = new URL(baseDomain);
      return `${targetObj.origin}${urlObj.pathname}${urlObj.search}`;
    } catch {
      return rawUrl;
    }
  }, [baseDomain]);

  // Opciones de destino adaptadas al rol
  const targetPathOptions = useMemo(() => {
    if (rol === 'docente') {
      return [
        { value: '/teacher/cases', label: 'Panel Docente: Gestión de Casos y Salas Clínicas (Recomendado)' },
        { value: '/teacher/analytics', label: 'Analítica de Cohorte, Psicometría e Índice IBF' },
        { value: '/cases', label: 'Catálogo General de Casos Clínicos (Vista Alumno)' },
        { value: '/benchmark', label: 'Benchmark Científico y Radar de Competencias' },
        { value: '/cases/case_preeclampsia_01', label: 'Caso: Preeclampsia Severa con Criterios de Gravedad' },
      ];
    }
    if (rol === 'administrador') {
      return [
        { value: '/admin/users', label: 'Consola de Administración de Usuarios (Recomendado)' },
        { value: '/admin/magic-links', label: 'Auditoría y Emisión de Magic Links' },
        { value: '/teacher/cases', label: 'Panel Docente de Cohortes' },
        { value: '/cases', label: 'Catálogo General de Casos Clínicos' },
      ];
    }
    return [
      { value: '/cases', label: 'Catálogo General de Casos Clínicos (Recomendado)' },
      { value: '/benchmark', label: 'Benchmark Científico y Radar de Competencias' },
      { value: '/cases/case_preeclampsia_01', label: 'Caso: Preeclampsia Severa con Criterios de Gravedad' },
      { value: '/cases/case_apendicitis_02', label: 'Caso: Apendicitis Aguda Complicada' },
      { value: '/cases/case_crisis_asmatica_03', label: 'Caso: Crisis Asmática Severa en Pediatría' },
      { value: '/cases/case_shock_septico_04', label: 'Caso: Shock Séptico de Origen Pulmonar' },
    ];
  }, [rol]);

  // Emisión principal (maneja tanto Lote atómico como Individual / Cohorte)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg(null);
    setSuccessNotice(null);

    try {
      if (modo === 'reutilizable' && emisionTipo === 'lote') {
        // Generación Atómica por Lote en Backend
        const batchPayload: MagicLinkBatchCreatePayload = {
          rol,
          base_name: batchPrefix.trim() || (rol === 'alumno' ? 'Estudiante' : 'Docente'),
          start_index: Number(batchStartIndex) || 1,
          count: Number(batchQuantity) || 1,
          duracion_horas: Number(duracionHoras),
          max_uses: 100,
          es_reutilizable: true,
          target_path: targetPath.trim() || (rol === 'docente' ? '/teacher/cases' : '/cases'),
          cohorte_id: 'general',
          restrict_domain: restrictDomain,
          base_url: baseDomain.trim() || undefined,
        };

        const batchResults = await authApi.createMagicLinksBatch(batchPayload);
        setRecentGenerated(batchResults);
        setSuccessNotice(`Se emitieron exitosamente ${batchResults.length} enlaces para el lote.`);
        fetchLinks();
      } else {
        // Generación Individual o de Cohorte
        const calculatedMaxUses = modo === 'unico' ? 1 : modo === 'reutilizable' ? 100 : Number(maxUses);
        const payload: MagicLinkCreatePayload = {
          rol,
          duracion_horas: Number(duracionHoras),
          max_uses: calculatedMaxUses,
          es_reutilizable: modo === 'reutilizable',
          target_path: targetPath.trim() || (rol === 'docente' ? '/teacher/cases' : '/cases'),
          cohorte_id: modo === 'cohorte' ? (cohorteId.trim() || 'general') : 'general',
          restrict_domain: restrictDomain,
          email: modo === 'unico' && email.trim() ? email.trim() : undefined,
          recipient_name: recipientName.trim() || undefined,
          base_url: baseDomain.trim() || undefined,
        };

        const result = await authApi.createMagicLink(payload);
        setRecentGenerated([result]);
        setSuccessNotice(`Enlace para ${result.recipient_name || 'evaluador'} emitido exitosamente.`);
        if (modo === 'unico') setEmail('');
        fetchLinks();
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setErrorMsg(error.response?.data?.detail || error.message || 'Error al emitir los Magic Links.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCopyUrl = (rawUrl: string, id: string) => {
    if (!rawUrl) return;
    const finalUrl = normalizeShareableUrl(rawUrl);
    navigator.clipboard.writeText(finalUrl);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 3000);
  };

  const buildInviteMessage = (link: MagicLinkRecord): string => {
    const finalUrl = normalizeShareableUrl(link.magic_link_url);
    const roleCapitalized = link.rol.charAt(0).toUpperCase() + link.rol.slice(1);
    const destName = link.target_path.includes('teacher') 
      ? 'Panel Docente (Casos, Salas y Analítica)' 
      : link.target_path.includes('admin') 
      ? 'Consola de Administración' 
      : 'Simulador Clínico (Casos y RAG MSP)';

    const recipientGreeting = link.recipient_name 
      ? `Estimado(a) ${link.recipient_name}:` 
      : 'Estimado(a) colega:';

    const modalityText = link.max_uses > 1 
      ? 'Acceso continuo reutilizable (puede ingresar múltiples veces durante la vigencia guardando su historial)'
      : 'Uso personal (1 solo acceso)';

    return `${recipientGreeting}\n\nLe comparto su enlace de acceso a la plataforma Ateneo+ (Simulador Clínico y Evaluación Médica con IA):\n\n- Rol asignado: ${roleCapitalized} (Acceso completo)\n- Destino clínico: ${destName}\n- Enlace directo (1 clic): ${finalUrl}\n- Modalidad: ${modalityText}\n- Vigencia: ${new Date(link.expires_at).toLocaleDateString()}\n\nPuede ingresar desde su navegador móvil o de escritorio cuantas veces necesite. No requiere contraseñas.`;
  };

  const handleCopyMessage = (link: MagicLinkRecord) => {
    const message = buildInviteMessage(link);
    navigator.clipboard.writeText(message);
    setCopiedMsgId(link.id);
    setTimeout(() => setCopiedMsgId(null), 3000);
  };

  const handleShareWhatsApp = (link: MagicLinkRecord) => {
    const message = buildInviteMessage(link);
    const encoded = encodeURIComponent(message);
    window.open(`https://api.whatsapp.com/send?text=${encoded}`, '_blank');
  };

  // Copiar todos los enlaces generados en un formato de lista estructurada
  const handleCopyAllLinks = () => {
    if (recentGenerated.length === 0) return;
    const header = `Enlaces de Acceso a Ateneo+ (Generados el ${new Date().toLocaleDateString()}):\n\n`;
    const lines = recentGenerated.map((item, idx) => {
      const shareUrl = normalizeShareableUrl(item.magic_link_url);
      const name = item.recipient_name || `Participante ${idx + 1}`;
      return `${idx + 1}. ${name} (${item.rol.toUpperCase()}): ${shareUrl}`;
    });
    const footer = `\n\nModalidad: Acceso continuo reutilizable | Vigencia: 7 días. Ingrese con 1 clic sin contraseñas.`;
    navigator.clipboard.writeText(header + lines.join('\n') + footer);
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 3000);
  };

  // Exportar los enlaces generados a archivo CSV
  const handleExportCSV = () => {
    if (recentGenerated.length === 0) return;
    const headers = ['Nombre / Identificador', 'Rol', 'URL de Acceso', 'Destino', 'Vigencia', 'Modalidad'];
    const rows = recentGenerated.map((item) => [
      `"${item.recipient_name || 'Invitado'}"`,
      `"${item.rol}"`,
      `"${normalizeShareableUrl(item.magic_link_url)}"`,
      `"${item.target_path}"`,
      `"${new Date(item.expires_at).toLocaleDateString()}"`,
      `"${item.max_uses > 1 ? 'Reutilizable' : '1 Solo uso'}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `ateneo_magic_links_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const confirmAndRevoke = async (linkId: string) => {
    setRevoking(true);
    try {
      await authApi.revokeMagicLink(linkId);
      setRevokeTargetId(null);
      setRecentGenerated((prev) => prev.filter((l) => l.id !== linkId));
      fetchLinks();
    } catch {
      setErrorMsg('No se pudo revocar el enlace.');
    } finally {
      setRevoking(false);
    }
  };

  const confirmAndPurge = async (linkId: string) => {
    try {
      await authApi.purgeMagicLink(linkId);
      setPurgeTargetId(null);
      setRecentGenerated((prev) => prev.filter((l) => l.id !== linkId));
      fetchLinks();
    } catch {
      setErrorMsg('No se pudo eliminar el enlace.');
    }
  };

  const handlePurgeAllRevoked = async () => {
    setPurgingRevoked(true);
    try {
      const res = await authApi.purgeRevokedLinks();
      setSuccessNotice(`Se eliminaron definitivamente ${res.eliminados} enlaces revocados.`);
      fetchLinks();
    } catch {
      setErrorMsg('Error al purgar los enlaces revocados.');
    } finally {
      setPurgingRevoked(false);
    }
  };

  // Filtrado de auditoría
  const filteredLinks = useMemo(() => {
    const now = new Date();
    return links.filter((item) => {
      const isExpired = new Date(item.expires_at) < now;
      const isExhausted = item.used_count >= item.max_uses;

      if (auditFilter === 'activos') {
        return !item.is_revoked && !isExpired && !isExhausted;
      }
      if (auditFilter === 'expirados') {
        return !item.is_revoked && (isExpired || isExhausted);
      }
      if (auditFilter === 'revocados') {
        return item.is_revoked;
      }
      return true;
    });
  }, [links, auditFilter]);

  const auditStats = useMemo(() => {
    const now = new Date();
    let activos = 0;
    let expirados = 0;
    let revocados = 0;
    links.forEach((l) => {
      if (l.is_revoked) {
        revocados++;
      } else if (new Date(l.expires_at) < now || l.used_count >= l.max_uses) {
        expirados++;
      } else {
        activos++;
      }
    });
    return { total: links.length, activos, expirados, revocados };
  }, [links]);

  return (
    <div className="space-y-8">
      {/* Tarjeta Principal de Configuración y Emisión */}
      <div className="bg-white rounded-[28px] p-6 sm:p-10 shadow-sm border-0">
        {/* Encabezado Principal */}
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-100 gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Link2 className="w-5 h-5 text-cyan-600" />
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                Emisión de Magic Links e Invitaciones Configurables
              </h2>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed max-w-2xl">
              Genera enlaces de acceso directo para evaluadores de prueba o cohortes. Cada persona accede con 1 clic sin contraseñas, conservando su progreso continuo.
            </p>
          </div>

          {/* Selector de Dominio Canónico */}
          <div className="flex items-center gap-2 self-start md:self-auto bg-slate-50 border border-slate-200/80 rounded-full px-3.5 py-1.5">
            <Globe className="w-3.5 h-3.5 text-cyan-600" />
            <span className="text-[11px] font-semibold text-slate-500">Dominio:</span>
            <select
              value={baseDomain}
              onChange={(e) => setBaseDomain(e.target.value)}
              className="text-xs text-slate-800 font-semibold bg-transparent border-none focus:outline-hidden cursor-pointer"
            >
              <option value="https://ateneo.doicela.dev">Producción (ateneo.doicela.dev)</option>
              <option value={detectedOrigin}>Local ({detectedOrigin})</option>
            </select>
          </div>
        </div>

        {errorMsg && (
          <div className="my-5 p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center gap-3 text-xs text-rose-800">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successNotice && (
          <div className="my-5 p-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-center gap-3 text-xs text-emerald-800">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successNotice}</span>
          </div>
        )}

        {/* Paso 1: Pestañas Planas de Rol (Underline Pattern del Sistema de Diseño) */}
        <div className="pt-6">
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
            1. Seleccione el Rol que otorgará el enlace
          </label>
          <div className="flex items-center gap-6 sm:gap-10 border-b border-slate-200">
            <button
              type="button"
              onClick={() => handleRoleChange('alumno')}
              className={`pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer -mb-[2px] ${
                rol === 'alumno'
                  ? 'border-cyan-600 text-cyan-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <GraduationCap className="w-4 h-4" />
              <span>Alumno</span>
            </button>
            <button
              type="button"
              onClick={() => handleRoleChange('docente')}
              className={`pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer -mb-[2px] ${
                rol === 'docente'
                  ? 'border-blue-600 text-blue-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Stethoscope className="w-4 h-4" />
              <span>Docente</span>
            </button>
            <button
              type="button"
              onClick={() => handleRoleChange('administrador')}
              className={`pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer -mb-[2px] ${
                rol === 'administrador'
                  ? 'border-indigo-600 text-indigo-700'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Shield className="w-4 h-4" />
              <span>Administrador</span>
            </button>
          </div>
        </div>

        {/* Paso 2: Selección de Modalidad en Tarjetas Claras */}
        <div className="pt-6">
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
            2. Tipo de Invitación y Frecuencia de Acceso
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <button
              type="button"
              onClick={() => {
                setModo('reutilizable');
                setMaxUses(100);
              }}
              className={`p-4 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                modo === 'reutilizable'
                  ? 'bg-cyan-50/40 border-cyan-500 ring-2 ring-cyan-500/20 shadow-xs'
                  : 'bg-slate-50/70 border-slate-200 hover:bg-slate-100/60'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-slate-900">
                    Reutilizable (Multi-ingreso)
                  </span>
                  <span className="text-[10px] font-bold text-cyan-800 bg-cyan-100/80 px-2 py-0.5 rounded-full">
                    Recomendado
                  </span>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Para evaluadores de prueba. Permite emitir 1 persona o un lote numerado (1, 2, 3...) con progreso guardado continuo.
                </p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => {
                setModo('unico');
                setMaxUses(1);
                setEmisionTipo('individual');
              }}
              className={`p-4 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                modo === 'unico'
                  ? 'bg-cyan-50/40 border-cyan-500 ring-2 ring-cyan-500/20 shadow-xs'
                  : 'bg-slate-50/70 border-slate-200 hover:bg-slate-100/60'
              }`}
            >
              <div>
                <div className="text-xs font-bold text-slate-900 mb-1.5">
                  1 Solo Uso (Acceso Único)
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Para evaluaciones de examen único. El enlace queda desactivado inmediatamente tras el primer ingreso exitoso.
                </p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => {
                setModo('cohorte');
                setMaxUses(10);
                setEmisionTipo('individual');
              }}
              className={`p-4 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                modo === 'cohorte'
                  ? 'bg-cyan-50/40 border-cyan-500 ring-2 ring-cyan-500/20 shadow-xs'
                  : 'bg-slate-50/70 border-slate-200 hover:bg-slate-100/60'
              }`}
            >
              <div>
                <div className="text-xs font-bold text-slate-900 mb-1.5">
                  Cohorte / Taller Grupal
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Un solo enlace compartido para 5, 10 o 50 personas. Cada participante ingresa con su correo universitario.
                </p>
              </div>
            </button>
          </div>
        </div>

        {/* Paso 3: Formulario Configurable de Destinatarios y Parámetros */}
        <form onSubmit={handleSubmit} className="pt-6 space-y-6">
          <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            3. Datos del Destinatario y Parámetros Clínicos
          </label>

          {/* Subselector de Emisión en Modo Reutilizable: Lote vs Individual */}
          {modo === 'reutilizable' && (
            <div className="bg-slate-50/80 p-3.5 rounded-2xl border border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <span className="text-xs font-bold text-slate-700">Modalidad de Emisión:</span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setEmisionTipo('lote')}
                  className={`py-1.5 px-3.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                    emisionTipo === 'lote'
                      ? 'bg-slate-900 text-white shadow-xs'
                      : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>Generación en Lote (Varios Evaluadores)</span>
                </button>
                <button
                  type="button"
                  onClick={() => setEmisionTipo('individual')}
                  className={`py-1.5 px-3.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                    emisionTipo === 'individual'
                      ? 'bg-slate-900 text-white shadow-xs'
                      : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <UserPlus className="w-3.5 h-3.5" />
                  <span>Individual (1 Solo Evaluador)</span>
                </button>
              </div>
            </div>
          )}

          {/* Formulario en caso de Lote */}
          {modo === 'reutilizable' && emisionTipo === 'lote' ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-start">
                {/* Prefijo Base */}
                <div>
                  <FloatingLabelInput
                    id="ml-batch-prefix"
                    type="text"
                    label="Prefijo o Etiqueta Base"
                    value={batchPrefix}
                    onChange={(e) => setBatchPrefix(e.target.value)}
                    placeholder="Estudiante"
                    required
                  />
                  <div className="flex items-center gap-1.5 mt-2">
                    <span className="text-[11px] text-slate-500 font-medium">Sugerencias:</span>
                    {(rol === 'alumno' ? ['Estudiante', 'Alumno', 'Evaluador'] : ['Docente', 'Profesor', 'Dr. Revisor']).map((sug) => (
                      <button
                        key={sug}
                        type="button"
                        onClick={() => setBatchPrefix(sug)}
                        className={`text-[11px] py-0.5 px-2 rounded-full cursor-pointer transition-colors ${
                          batchPrefix === sug ? 'bg-cyan-700 text-white font-semibold' : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                        }`}
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Número de Inicio (Permite arrancar desde el 1 o desde el correlativo) */}
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1.5">
                    Iniciar Numeración en:
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min={1}
                      max={9999}
                      value={batchStartIndex}
                      onChange={(e) => setBatchStartIndex(Math.max(1, parseInt(e.target.value, 10) || 1))}
                      className="w-24 py-3 px-3.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-cyan-500"
                    />
                    <button
                      type="button"
                      onClick={() => setBatchStartIndex(1)}
                      className={`text-xs py-2 px-3 rounded-xl border transition-colors cursor-pointer ${
                        batchStartIndex === 1
                          ? 'bg-slate-900 text-white border-slate-900 font-bold'
                          : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                      }`}
                      title="Reiniciar numeración desde el 1"
                    >
                      Iniciar en 1
                    </button>
                    {nextAvailableIndex > 1 && (
                      <button
                        type="button"
                        onClick={() => setBatchStartIndex(nextAvailableIndex)}
                        className={`text-xs py-2 px-3 rounded-xl border transition-colors cursor-pointer ${
                          batchStartIndex === nextAvailableIndex
                            ? 'bg-slate-900 text-white border-slate-900 font-bold'
                            : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                        }`}
                        title={`Continuar desde el siguiente disponible (#${nextAvailableIndex})`}
                      >
                        Continuar (#{nextAvailableIndex})
                      </button>
                    )}
                  </div>
                  <span className="block text-[11px] text-slate-400 mt-1">
                    Puedes empezar desde el <strong>1</strong> o continuar desde donde te quedaste.
                  </span>
                </div>

                {/* Cantidad a Generar en el Lote */}
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1.5">
                    Cantidad de Enlaces en este Lote:
                  </label>
                  <div className="flex items-center gap-2">
                    <div className="inline-flex items-center bg-slate-50 border border-slate-300 rounded-xl px-2 py-1.5">
                      <button
                        type="button"
                        onClick={() => setBatchQuantity((q) => Math.max(1, q - 1))}
                        className="w-7 h-7 flex items-center justify-center text-slate-700 hover:text-slate-900 hover:bg-slate-200/80 rounded-lg transition-colors cursor-pointer text-sm font-bold"
                        title="Reducir cantidad"
                      >
                        -
                      </button>
                      <input
                        type="number"
                        min={1}
                        max={50}
                        value={batchQuantity}
                        onChange={(e) => setBatchQuantity(Math.min(50, Math.max(1, parseInt(e.target.value, 10) || 1)))}
                        className="w-12 text-center font-bold text-slate-900 bg-transparent border-none focus:outline-hidden text-xs py-0.5"
                      />
                      <button
                        type="button"
                        onClick={() => setBatchQuantity((q) => Math.min(50, q + 1))}
                        className="w-7 h-7 flex items-center justify-center text-slate-700 hover:text-slate-900 hover:bg-slate-200/80 rounded-lg transition-colors cursor-pointer text-sm font-bold"
                        title="Aumentar cantidad"
                      >
                        +
                      </button>
                    </div>

                    <div className="flex items-center gap-1">
                      {[1, 2, 3, 5, 10].map((num) => (
                        <button
                          key={num}
                          type="button"
                          onClick={() => setBatchQuantity(num)}
                          className={`text-xs py-1.5 px-2.5 rounded-lg font-semibold transition-all cursor-pointer ${
                            batchQuantity === num
                              ? 'bg-cyan-700 text-white shadow-xs'
                              : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                          }`}
                        >
                          {num}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Caja de Previsualización en Vivo del Lote */}
              <div className="p-4 bg-cyan-50/50 border border-cyan-200/80 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                  <div className="flex items-center gap-2 font-bold text-cyan-950 mb-1">
                    <Sparkles className="w-4 h-4 text-cyan-700 shrink-0" />
                    <span>
                      Vista previa del lote: {batchQuantity} {batchQuantity === 1 ? 'enlace' : 'enlaces'}
                    </span>
                  </div>
                  <p className="text-cyan-800">
                    Se generará: <strong>&quot;{batchPrefix} {batchStartIndex}&quot;</strong>
                    {batchQuantity > 1 && (
                      <> hasta <strong>&quot;{batchPrefix} {batchStartIndex + batchQuantity - 1}&quot;</strong></>
                    )}
                    . Cada enlace tendrá su propia cuenta independiente y acceso continuo reutilizable.
                  </p>
                </div>
                <div className="text-[11px] text-cyan-900 font-semibold bg-white/80 px-3 py-1.5 rounded-xl border border-cyan-100 self-start sm:self-auto shrink-0">
                  Total: {batchQuantity} cuentas provisionadas
                </div>
              </div>
            </div>
          ) : (
            /* Formulario Individual o de Cohorte */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
              {/* Nombre del Destinatario con Chips de Selección Rápida */}
              <div>
                <FloatingLabelInput
                  id="ml-recipient"
                  type="text"
                  label={modo === 'cohorte' ? 'Nombre de la Cohorte o Rotación' : 'Nombre o Referencia del Evaluador'}
                  value={recipientName}
                  onChange={(e) => setRecipientName(e.target.value)}
                  placeholder={modo === 'cohorte' ? 'Rotación Pediatría Paralelo A' : (rol === 'docente' ? 'Docente 1' : 'Estudiante 1')}
                  required
                />

                {modo !== 'cohorte' && (
                  <div className="flex flex-wrap items-center gap-1.5 mt-2.5">
                    <span className="text-[11px] text-slate-500 font-medium">Asignar con 1 clic:</span>
                    {(rol === 'alumno' 
                      ? ['Estudiante 1', 'Estudiante 2', 'Estudiante 3', 'Estudiante 4', 'Estudiante 5']
                      : ['Docente 1', 'Docente 2', 'Docente 3', 'Dr. Revisor Clínico']
                    ).map((quickName) => (
                      <button
                        key={quickName}
                        type="button"
                        onClick={() => setRecipientName(quickName)}
                        className={`text-xs py-1 px-2.5 rounded-full font-medium transition-all cursor-pointer ${
                          recipientName === quickName
                            ? 'bg-slate-900 text-white shadow-xs'
                            : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                        }`}
                      >
                        {quickName}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Correo Opcional o Cupo */}
              {modo === 'unico' ? (
                <FloatingLabelInput
                  id="ml-email"
                  type="email"
                  label="Correo Institucional Específico (Opcional)"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="usuario@ateneo.edu.ec (vacío para express)"
                />
              ) : modo === 'cohorte' ? (
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1.5">
                    Cupo Máximo de Participantes
                  </label>
                  <select
                    value={maxUses}
                    onChange={(e) => setMaxUses(Number(e.target.value))}
                    className="w-full py-3.5 px-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 font-medium focus:outline-hidden focus:ring-2 focus:ring-cyan-500 cursor-pointer"
                  >
                    <option value={5}>Hasta 5 participantes</option>
                    <option value={10}>Hasta 10 participantes</option>
                    <option value={25}>Hasta 25 participantes</option>
                    <option value={50}>Hasta 50 participantes</option>
                    <option value={100}>Hasta 100 participantes</option>
                  </select>
                </div>
              ) : (
                <div className="py-3 px-4 bg-slate-50 border border-slate-200/80 rounded-2xl text-xs text-slate-600 leading-relaxed">
                  <span className="font-semibold text-slate-800 block mb-0.5">Identidad Aprovisionada:</span>
                  Al generar el enlace, se creará la cuenta express para <strong className="text-cyan-800">{recipientName || 'el evaluador'}</strong> permitiéndole ingresar todas las veces que desee durante los días de vigencia.
                </div>
              )}
            </div>
          )}

          {modo === 'cohorte' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FloatingLabelInput
                id="ml-cohorte-id"
                type="text"
                label="Identificador Técnico de la Cohorte"
                value={cohorteId}
                onChange={(e) => setCohorteId(e.target.value)}
                placeholder="general"
              />
            </div>
          )}

          {/* Fila: Vigencia y Destino Clínico */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Vigencia del Enlace
              </label>
              <select
                value={duracionHoras}
                onChange={(e) => setDuracionHoras(Number(e.target.value))}
                className="w-full py-3 px-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 font-semibold focus:outline-hidden focus:ring-2 focus:ring-cyan-500 cursor-pointer"
              >
                <option value={168}>7 días (1 semana - Recomendado)</option>
                <option value={720}>30 días (1 mes)</option>
                <option value={72}>72 horas (3 días)</option>
                <option value={24}>24 horas (1 día)</option>
              </select>
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Destino Clínico de Aterrizaje
              </label>
              <select
                value={targetPath}
                onChange={(e) => setTargetPath(e.target.value)}
                className="w-full py-3 px-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 font-semibold focus:outline-hidden focus:ring-2 focus:ring-cyan-500 cursor-pointer"
              >
                {targetPathOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Barra de Acciones y Botón Principal de Emisión */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-100">
            <label className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={restrictDomain}
                onChange={(e) => setRestrictDomain(e.target.checked)}
                className="w-4 h-4 rounded text-cyan-600 focus:ring-cyan-500 cursor-pointer"
              />
              <span>Exigir correo institucional del tenant</span>
            </label>

            <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
              {/* Botón Principal con Gradiente Ateneo+ */}
              <button
                type="submit"
                disabled={submitting}
                className="w-full sm:w-auto py-3.5 px-8 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-700 hover:via-blue-700 hover:to-indigo-700 text-white font-semibold text-xs rounded-full transition-all shadow-md shadow-blue-500/20 hover:shadow-lg hover:shadow-blue-500/30 active:scale-[0.99] flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-white" />
                    <span>
                      {modo === 'reutilizable' && emisionTipo === 'lote' 
                        ? `Generando lote de ${batchQuantity}...` 
                        : 'Emitiendo acceso...'}
                    </span>
                  </>
                ) : (
                  <>
                    {modo === 'reutilizable' && emisionTipo === 'lote' ? (
                      <>
                        <Layers className="w-4 h-4" />
                        <span>
                          Generar Lote de {batchQuantity} ({batchPrefix} {batchStartIndex}{batchQuantity > 1 ? ` a ${batchStartIndex + batchQuantity - 1}` : ''})
                        </span>
                      </>
                    ) : (
                      <>
                        <Link2 className="w-4 h-4" />
                        <span>Generar Magic Link Seguro</span>
                      </>
                    )}
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Enlaces Generados Recientemente: Tarjetas Listas para Compartir y Acciones Masivas */}
      {recentGenerated.length > 0 && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-600" />
              <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
                Enlaces Listos para Compartir ({recentGenerated.length})
              </h3>
            </div>

            {/* Acciones de Lote: Copiar Todos y Exportar CSV */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleCopyAllLinks}
                className="py-2 px-3.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer shadow-xs"
                title="Copiar lista consolidada para pegar en WhatsApp o Teams"
              >
                {copiedAll ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Lista Copiada</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copiar Todos los Enlaces</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleExportCSV}
                className="py-2 px-3.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer shadow-xs"
                title="Descargar reporte en archivo CSV"
              >
                <Download className="w-3.5 h-3.5 text-cyan-600" />
                <span>Exportar CSV</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentGenerated.map((item) => {
              const finalShareUrl = normalizeShareableUrl(item.magic_link_url);
              return (
                <div
                  key={item.id}
                  className="bg-white rounded-2xl p-5 shadow-xs border border-cyan-100 flex flex-col justify-between space-y-4"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-bold text-slate-900">
                        {item.recipient_name || 'Evaluador Invitado'}
                      </span>
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        item.rol === 'docente' 
                          ? 'bg-blue-50 text-blue-700' 
                          : item.rol === 'administrador'
                          ? 'bg-purple-50 text-purple-700'
                          : 'bg-cyan-50 text-cyan-700'
                      }`}>
                        {item.rol}
                      </span>
                    </div>

                    <div className="text-xs text-slate-500 space-y-1 mb-3">
                      <div className="flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span>Modalidad: <strong>{item.max_uses > 1 ? 'Reutilizable (Multi-ingreso)' : '1 Solo uso'}</strong></span>
                      </div>
                      <div className="text-[11px] text-slate-400">
                        Vigencia: hasta {new Date(item.expires_at).toLocaleDateString()}
                      </div>
                    </div>

                    {/* Campo de URL de solo lectura */}
                    <div className="bg-slate-50 rounded-xl p-2 border border-slate-200/80 mb-3">
                      <input
                        type="text"
                        readOnly
                        value={finalShareUrl}
                        className="w-full text-xs font-mono text-slate-700 bg-transparent border-none focus:outline-hidden"
                      />
                    </div>
                  </div>

                  {/* Botones Directos de Compartición */}
                  <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => handleCopyUrl(item.magic_link_url, item.id)}
                      className="flex-1 py-2 px-3 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                    >
                      {copiedId === item.id ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span>Copiado</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span>Copiar Link</span>
                        </>
                      )}
                    </button>

                    <button
                      type="button"
                      onClick={() => handleShareWhatsApp(item)}
                      className="py-2 px-3 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                      title="Enviar por WhatsApp"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      <span>WhatsApp</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => handleCopyMessage(item)}
                      className="p-2 border border-slate-200 hover:bg-slate-100 text-slate-600 rounded-xl transition-colors cursor-pointer"
                      title="Copiar invitación con texto formal"
                    >
                      {copiedMsgId === item.id ? (
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                      ) : (
                        <Share2 className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tabla de Auditoría General de Enlaces Emitidos */}
      <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-sm border-0">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 mb-4 gap-3">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-slate-600" />
            <h3 className="text-sm font-bold text-slate-800 tracking-tight">
              Auditoría y Control de Magic Links Emitidos
            </h3>
          </div>

          <div className="flex items-center gap-3">
            {auditStats.revocados > 0 && (
              <button
                type="button"
                onClick={handlePurgeAllRevoked}
                disabled={purgingRevoked}
                className="py-1.5 px-3 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
                title="Elimina permanentemente de la base de datos todos los enlaces revocados"
              >
                <Trash2 className="w-3.5 h-3.5 text-rose-600" />
                <span>{purgingRevoked ? 'Limpiando...' : `Limpiar Revocados (${auditStats.revocados})`}</span>
              </button>
            )}

            <button
              onClick={fetchLinks}
              className="p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
              title="Refrescar lista"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingLinks ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Pestañas de Filtrado de Auditoría */}
        <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-1 text-xs">
          <span className="text-slate-400 font-semibold flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5" />
            <span>Filtro:</span>
          </span>
          {[
            { id: 'todos', label: `Todos (${auditStats.total})` },
            { id: 'activos', label: `Activos (${auditStats.activos})` },
            { id: 'expirados', label: `Agotados / Vencidos (${auditStats.expirados})` },
            { id: 'revocados', label: `Revocados (${auditStats.revocados})` },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setAuditFilter(tab.id as typeof auditFilter)}
              className={`py-1 px-3 rounded-full font-medium transition-colors cursor-pointer whitespace-nowrap ${
                auditFilter === tab.id
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {linksError ? (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800">
            {linksError}
          </div>
        ) : filteredLinks.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400">
            No hay Magic Links que coincidan con el filtro seleccionado.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-[#f0f4f9] text-slate-800 font-medium uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="px-4 py-3 rounded-l-xl">Destinatario / Evaluador</th>
                  <th className="px-4 py-3">Rol</th>
                  <th className="px-4 py-3">Destino Clínico</th>
                  <th className="px-4 py-3 text-center">Accesos</th>
                  <th className="px-4 py-3">Vence</th>
                  <th className="px-4 py-3 text-center">Estado</th>
                  <th className="px-4 py-3 text-right rounded-r-xl">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredLinks.map((item) => {
                  const isExpired = new Date(item.expires_at) < new Date();
                  const isExhausted = item.used_count >= item.max_uses;
                  let statusBadge = 'bg-emerald-50 text-emerald-700';
                  let statusText = 'Activo';

                  if (item.is_revoked) {
                    statusBadge = 'bg-rose-50 text-rose-700';
                    statusText = 'Revocado';
                  } else if (isExhausted) {
                    statusBadge = 'bg-slate-100 text-slate-600';
                    statusText = 'Agotado';
                  } else if (isExpired) {
                    statusBadge = 'bg-amber-50 text-amber-700';
                    statusText = 'Vencido';
                  }

                  const isUsable = !item.is_revoked && !isExpired && !isExhausted;
                  const isReusable = item.max_uses > 1 && (!item.cohorte_id || item.cohorte_id === 'general');

                  return (
                    <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-4 py-3.5 font-medium text-slate-900">
                        {item.recipient_name || item.email || 'Acceso Directo (Invitado)'}
                        {item.email && (
                          <div className="text-[11px] text-slate-400 font-normal">{item.email}</div>
                        )}
                      </td>
                      <td className="px-4 py-3.5 capitalize font-medium">
                        <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-semibold ${
                          item.rol === 'docente' 
                            ? 'bg-blue-50 text-blue-700' 
                            : item.rol === 'administrador' 
                            ? 'bg-purple-50 text-purple-700' 
                            : 'bg-cyan-50 text-cyan-700'
                        }`}>
                          {item.rol}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-slate-500 font-mono text-[11px]">
                        {item.target_path}
                      </td>
                      <td className="px-4 py-3.5 text-center font-semibold text-slate-700">
                        {isReusable ? (
                          <span className="inline-flex items-center gap-1 text-[11px] text-cyan-800 bg-cyan-50 px-2 py-0.5 rounded-md font-medium">
                            {item.used_count} usos (Reutilizable)
                          </span>
                        ) : (
                          <span>{item.used_count} / {item.max_uses}</span>
                        )}
                      </td>
                      <td className="px-4 py-3.5 text-slate-500 text-[11px]">
                        {new Date(item.expires_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3.5 text-center">
                        <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-semibold ${statusBadge}`}>
                          {statusText}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {isUsable && (
                            <>
                              <button
                                type="button"
                                onClick={() => handleCopyUrl(item.magic_link_url, item.id)}
                                className="p-1.5 text-cyan-700 hover:bg-cyan-50 rounded-lg transition-colors cursor-pointer"
                                title="Copiar enlace"
                              >
                                {copiedId === item.id ? (
                                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                                ) : (
                                  <Copy className="w-3.5 h-3.5" />
                                )}
                              </button>

                              <button
                                type="button"
                                onClick={() => handleCopyMessage(item)}
                                className="p-1.5 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
                                title="Copiar invitación con texto para WhatsApp"
                              >
                                {copiedMsgId === item.id ? (
                                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                                ) : (
                                  <Share2 className="w-3.5 h-3.5" />
                                )}
                              </button>

                              <button
                                type="button"
                                onClick={() => handleShareWhatsApp(item)}
                                className="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors cursor-pointer"
                                title="Abrir en WhatsApp"
                              >
                                <ExternalLink className="w-3.5 h-3.5" />
                              </button>
                            </>
                          )}

                          {/* Botón Revocar (para enlaces activos) */}
                          {isUsable && (
                            revokeTargetId === item.id ? (
                              <div className="inline-flex items-center gap-1.5 bg-rose-50 p-1 rounded-lg border border-rose-200">
                                <span className="text-[10px] text-rose-800 font-semibold pl-1">¿Revocar?</span>
                                <button
                                  type="button"
                                  onClick={() => confirmAndRevoke(item.id)}
                                  disabled={revoking}
                                  className="px-2 py-0.5 bg-rose-600 text-white rounded text-[10px] font-medium hover:bg-rose-700 disabled:opacity-50 cursor-pointer"
                                >
                                  {revoking ? '...' : 'Sí'}
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setRevokeTargetId(null)}
                                  className="px-2 py-0.5 bg-slate-200 text-slate-700 rounded text-[10px] font-medium hover:bg-slate-300 cursor-pointer"
                                >
                                  No
                                </button>
                              </div>
                            ) : (
                              <button
                                type="button"
                                onClick={() => setRevokeTargetId(item.id)}
                                className="text-rose-600 hover:text-rose-800 text-[11px] font-medium inline-flex items-center gap-1 hover:underline cursor-pointer ml-1"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                                <span>Revocar</span>
                              </button>
                            )
                          )}

                          {/* Botón Eliminar Físicamente (para enlaces ya revocados o vencidos) */}
                          {!isUsable && (
                            purgeTargetId === item.id ? (
                              <div className="inline-flex items-center gap-1.5 bg-slate-100 p-1 rounded-lg border border-slate-300">
                                <span className="text-[10px] text-slate-800 font-semibold pl-1">¿Eliminar?</span>
                                <button
                                  type="button"
                                  onClick={() => confirmAndPurge(item.id)}
                                  className="px-2 py-0.5 bg-rose-600 text-white rounded text-[10px] font-medium hover:bg-rose-700 cursor-pointer"
                                >
                                  Sí
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setPurgeTargetId(null)}
                                  className="px-2 py-0.5 bg-slate-200 text-slate-700 rounded text-[10px] font-medium hover:bg-slate-300 cursor-pointer"
                                >
                                  No
                                </button>
                              </div>
                            ) : (
                              <button
                                type="button"
                                onClick={() => setPurgeTargetId(item.id)}
                                className="text-slate-400 hover:text-rose-600 text-[11px] font-medium inline-flex items-center gap-1 hover:underline cursor-pointer ml-1"
                                title="Eliminar registro definitivamente"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                                <span>Eliminar</span>
                              </button>
                            )
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default MagicLinkGeneratorCard;
