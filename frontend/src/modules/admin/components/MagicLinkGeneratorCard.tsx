import React, { useState, useEffect, useCallback } from 'react';
import { 
  Link2, 
  Copy, 
  Check, 
  Trash2, 
  Users, 
  Shield, 
  AlertCircle,
  Loader2,
  RefreshCw
} from 'lucide-react';
import authApi from '../../auth/api/authApi';
import type { MagicLinkRecord, MagicLinkCreatePayload } from '../../../types';
import FloatingLabelInput from '../../../core/ui/FloatingLabelInput';

/**
 * Componente Institucional: Generador y Gestor de Magic Links e Invitaciones Configurables (Ateneo+)
 * Permite a los administradores emitir accesos directos para pruebas clínicas, cohortes y docentes.
 * Diseño sobrio clínico Material 3 Canvas sin emojis.
 */
export const MagicLinkGeneratorCard: React.FC = () => {
  // Lista de enlaces y estado de carga
  const [links, setLinks] = useState<MagicLinkRecord[]>([]);
  const [loadingLinks, setLoadingLinks] = useState<boolean>(true);
  const [linksError, setLinksError] = useState<string | null>(null);

  // Parámetros configurables del formulario
  const [rol, setRol] = useState<'alumno' | 'docente' | 'administrador'>('alumno');
  const [modo, setModo] = useState<'nominativo' | 'cohorte'>('nominativo');
  const [email, setEmail] = useState<string>('');
  const [recipientName, setRecipientName] = useState<string>('');
  const [duracionHoras, setDuracionHoras] = useState<number>(72);
  const [maxUses, setMaxUses] = useState<number>(1);
  const [targetPath, setTargetPath] = useState<string>('/cases');
  const [cohorteId, setCohorteId] = useState<string>('general');
  const [restrictDomain, setRestrictDomain] = useState<boolean>(false);

  // Estado de envío y enlace generado reciente
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [generatedLink, setGeneratedLink] = useState<MagicLinkRecord | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [revokeTargetId, setRevokeTargetId] = useState<string | null>(null);
  const [revoking, setRevoking] = useState<boolean>(false);

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

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg(null);

    const payload: MagicLinkCreatePayload = {
      rol,
      duracion_horas: Number(duracionHoras),
      max_uses: modo === 'nominativo' ? 1 : Number(maxUses),
      target_path: targetPath.trim() || '/cases',
      cohorte_id: cohorteId.trim() || 'general',
      restrict_domain: restrictDomain,
      email: modo === 'nominativo' && email.trim() ? email.trim() : undefined,
      recipient_name: recipientName.trim() || undefined,
    };

    try {
      const result = await authApi.createMagicLink(payload);
      setGeneratedLink(result);
      if (modo === 'nominativo') setEmail('');
      setRecipientName('');
      fetchLinks();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setErrorMsg(error.response?.data?.detail || error.message || 'Error al emitir el Magic Link');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCopy = (url: string, id: string) => {
    if (!url) return;
    navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 3000);
  };

  const confirmAndRevoke = async (linkId: string) => {
    setRevoking(true);
    try {
      await authApi.revokeMagicLink(linkId);
      setRevokeTargetId(null);
      fetchLinks();
    } catch {
      setErrorMsg('No se pudo revocar el enlace.');
    } finally {
      setRevoking(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Tarjeta Generadora de Enlaces */}
      <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/80">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-6">
          <div className="flex items-center gap-3">
            <Link2 className="w-5 h-5 text-cyan-600" />
            <div>
              <h2 className="text-lg font-semibold text-slate-800 tracking-tight">
                Emisión de Magic Links e Invitaciones Configurables
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Genera accesos temporales firmados con hash SHA-256 para evaluar casos sin requerir registro previo.
              </p>
            </div>
          </div>
        </div>

        {errorMsg && (
          <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center gap-3 text-xs text-rose-800">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleGenerate} className="space-y-6">
          {/* Fila 1: Rol y Modalidad */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Rol Institucional Otorgado
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['alumno', 'docente', 'administrador'] as const).map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => setRol(r)}
                    className={`py-2 px-3 rounded-xl text-xs font-medium capitalize border transition-all ${
                      rol === r
                        ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                        : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Tipo de Audiencia
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setModo('nominativo');
                    setMaxUses(1);
                  }}
                  className={`py-2 px-3 rounded-xl text-xs font-medium border transition-all ${
                    modo === 'nominativo'
                      ? 'bg-cyan-600 text-white border-cyan-600 shadow-xs'
                      : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  Nominativo (1 persona)
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setModo('cohorte');
                    if (maxUses === 1) setMaxUses(10);
                  }}
                  className={`py-2 px-3 rounded-xl text-xs font-medium border transition-all ${
                    modo === 'cohorte'
                      ? 'bg-cyan-600 text-white border-cyan-600 shadow-xs'
                      : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  Cohorte / Taller (Grupo)
                </button>
              </div>
            </div>
          </div>

          {/* Fila 2: Destinatario o Etiqueta */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {modo === 'nominativo' ? (
              <FloatingLabelInput
                id="ml-email"
                type="email"
                label="Correo Institucional del Destinatario"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="docente.invitado@uce.edu.ec"
              />
            ) : (
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1.5">
                  Límite de Canjes (Cupo Máximo)
                </label>
                <select
                  value={maxUses}
                  onChange={(e) => setMaxUses(Number(e.target.value))}
                  className="w-full py-3 px-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 font-medium focus:outline-hidden focus:ring-2 focus:ring-cyan-500"
                >
                  <option value={5}>Hasta 5 participantes</option>
                  <option value={10}>Hasta 10 participantes</option>
                  <option value={25}>Hasta 25 participantes</option>
                  <option value={50}>Hasta 50 participantes</option>
                  <option value={100}>Hasta 100 participantes</option>
                </select>
              </div>
            )}

            <FloatingLabelInput
              id="ml-recipient"
              type="text"
              label={modo === 'nominativo' ? 'Nombre o Referencia (Opcional)' : 'Nombre de la Cohorte o Rotación'}
              value={recipientName}
              onChange={(e) => setRecipientName(e.target.value)}
              placeholder={modo === 'nominativo' ? 'Dr. Carlos Andrade' : 'Gineco-Obstetricia Paralelo A'}
            />
          </div>

          {modo === 'cohorte' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FloatingLabelInput
                id="ml-cohorte-id"
                type="text"
                label="Identificador Técnico de Cohorte / Grupo"
                value={cohorteId}
                onChange={(e) => setCohorteId(e.target.value)}
                placeholder="general"
              />
            </div>
          )}

          {/* Fila 3: Vigencia, Destino y Restricciones */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Vigencia del Enlace (TTL)
              </label>
              <select
                value={duracionHoras}
                onChange={(e) => setDuracionHoras(Number(e.target.value))}
                className="w-full py-3 px-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 font-medium focus:outline-hidden focus:ring-2 focus:ring-cyan-500"
              >
                <option value={12}>12 horas</option>
                <option value={24}>24 horas (1 día)</option>
                <option value={48}>48 horas (2 días)</option>
                <option value={72}>72 horas (3 días)</option>
                <option value={168}>7 días (1 semana)</option>
                <option value={336}>14 días (2 semanas)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">
                Destino Clínico de Aterrizaje
              </label>
              <select
                value={targetPath}
                onChange={(e) => setTargetPath(e.target.value)}
                className="w-full py-3 px-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 font-medium focus:outline-hidden focus:ring-2 focus:ring-cyan-500"
              >
                <option value="/cases">Catálogo General de Casos</option>
                <option value="/cases/case_preeclampsia_01">Caso: Preeclampsia Severa con Criterios de Gravedad</option>
                <option value="/cases/case_apendicitis_02">Caso: Apendicitis Aguda Complicada</option>
                <option value="/cases/case_crisis_asmatica_03">Caso: Crisis Asmática Severa en Pediatría</option>
                <option value="/cases/case_shock_septico_04">Caso: Shock Séptico de Origen Pulmonar</option>
              </select>
            </div>

            <div className="flex flex-col justify-end">
              <label className="flex items-center gap-2.5 p-3 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-100 transition-colors">
                <input
                  type="checkbox"
                  checked={restrictDomain}
                  onChange={(e) => setRestrictDomain(e.target.checked)}
                  className="rounded-sm border-slate-300 text-cyan-600 focus:ring-cyan-500 h-4 w-4"
                />
                <span className="text-xs text-slate-700 font-medium">
                  Exigir correo institucional del tenant
                </span>
              </label>
            </div>
          </div>

          {/* Botón de Emisión */}
          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="py-3 px-6 rounded-full bg-slate-900 text-white font-medium text-xs hover:bg-slate-800 transition-all shadow-xs flex items-center gap-2 disabled:opacity-60 cursor-pointer"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generando enlace seguro...</span>
                </>
              ) : (
                <>
                  <Link2 className="w-4 h-4" />
                  <span>Generar Magic Link Seguro</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Modal / Caja de Enlace Generado Reciente */}
        {generatedLink && (
          <div className="mt-8 p-5 bg-gradient-to-r from-cyan-50/70 to-blue-50/70 border border-cyan-200 rounded-2xl animate-fadeIn">
            <div className="flex items-center justify-between gap-4 mb-2">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-cyan-700" />
                <span className="text-xs font-bold text-cyan-950 uppercase tracking-wider">
                  Enlace de Acceso Generado Exitosamente
                </span>
              </div>
              <span className="text-[11px] font-medium text-cyan-800 bg-cyan-100 px-2.5 py-0.5 rounded-full">
                Rol: <strong className="capitalize">{generatedLink.rol}</strong> &bull; Cupo: {generatedLink.max_uses}
              </span>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 mt-3">
              <input
                type="text"
                readOnly
                value={generatedLink.magic_link_url}
                className="w-full bg-white border border-cyan-300 text-xs text-slate-800 font-mono py-2.5 px-3.5 rounded-xl select-all focus:outline-hidden"
              />
              <button
                type="button"
                onClick={() => handleCopy(generatedLink.magic_link_url, generatedLink.id)}
                className="px-4 py-2.5 bg-cyan-700 hover:bg-cyan-800 text-white text-xs font-medium rounded-xl flex items-center justify-center gap-2 shrink-0 transition-colors shadow-xs cursor-pointer"
              >
                {copiedId === generatedLink.id ? (
                  <>
                    <Check className="w-4 h-4" />
                    <span>Copiado</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    <span>Copiar Enlace</span>
                  </>
                )}
              </button>
            </div>

            <p className="text-[11px] text-slate-500 mt-2.5">
              Válido hasta: {new Date(generatedLink.expires_at).toLocaleString()} &bull; Destino: {generatedLink.target_path}
            </p>
          </div>
        )}
      </div>

      {/* Tabla de Auditoría de Enlaces Activos */}
      <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/80">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-slate-600" />
            <h3 className="text-sm font-semibold text-slate-800">
              Auditoría y Control de Magic Links Emitidos
            </h3>
          </div>
          <button
            onClick={fetchLinks}
            className="p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition-colors"
            title="Refrescar lista"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingLinks ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {linksError ? (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800">
            {linksError}
          </div>
        ) : links.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400">
            No hay Magic Links emitidos en esta institución.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-[#f0f4f9] text-slate-800 font-medium uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="px-4 py-3 rounded-l-xl">Destinatario / Cohorte</th>
                  <th className="px-4 py-3">Rol</th>
                  <th className="px-4 py-3">Destino Clínico</th>
                  <th className="px-4 py-3 text-center">Usos</th>
                  <th className="px-4 py-3">Vence</th>
                  <th className="px-4 py-3 text-center">Estado</th>
                  <th className="px-4 py-3 text-right rounded-r-xl">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {links.map((item) => {
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

                  return (
                    <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-4 py-3.5 font-medium text-slate-900">
                        {item.recipient_name || item.email || 'Enlace Grupal Anónimo'}
                        {item.email && item.recipient_name && (
                          <div className="text-[11px] text-slate-400 font-normal">{item.email}</div>
                        )}
                      </td>
                      <td className="px-4 py-3.5 capitalize font-medium">
                        {item.rol}
                      </td>
                      <td className="px-4 py-3.5 text-slate-500 font-mono text-[11px]">
                        {item.target_path}
                      </td>
                      <td className="px-4 py-3.5 text-center font-semibold text-slate-700">
                        {item.used_count} / {item.max_uses}
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
                        {!item.is_revoked && !isExpired && !isExhausted && (
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
                              className="text-rose-600 hover:text-rose-800 text-[11px] font-medium inline-flex items-center gap-1 hover:underline cursor-pointer"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                              <span>Revocar</span>
                            </button>
                          )
                        )}
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
