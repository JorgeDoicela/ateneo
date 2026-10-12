import React from 'react';
import MagicLinkGeneratorCard from '../components/MagicLinkGeneratorCard';

/**
 * Vista Dedicada: Gestión de Magic Links e Invitaciones Institucionales (Ateneo+)
 * Permite a las autoridades emitir credenciales temporales de un solo clic
 * para estudiantes, rotaciones clínicas y evaluadores externos.
 */
export const AdminMagicLinksPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn">
      <MagicLinkGeneratorCard />
    </div>
  );
};

export default AdminMagicLinksPage;
