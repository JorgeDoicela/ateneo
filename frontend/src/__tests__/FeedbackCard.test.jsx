import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import FeedbackCard from '../modules/evaluation/components/FeedbackCard';

// Mock de useAuth
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'usr_01', nombre: 'Estudiante Test', rol: 'alumno' }
  })
}));

// Mock de SkillRadarChart para aislar la prueba
vi.mock('../modules/analytics/components/SkillRadarChart', () => ({
  default: () => <div data-testid="skill-radar-mock">Mock Radar Chart</div>
}));

// Mock de PdfViewerModal
vi.mock('../modules/evaluation/components/PdfViewerModal', () => ({
  default: () => null
}));

describe('Componente FeedbackCard (Ateneo+)', () => {
  const mockResult = {
    score: 8.5,
    score_max: 10,
    aciertos: [
      'Identificación correcta de signos de alarma de Dengue',
      'Solicitud adecuada de biometría hemática completa'
    ],
    omisiones: [
      'Omisión de esquema de reposición hídrica intravenosa inicial'
    ],
    competencias_deficientes: [
      { eje: 'tratamiento', descripcion: 'Dosis exacta de solución salina isotónica' }
    ],
    cita_normativa: {
      guia: 'Guía de Práctica Clínica Dengue',
      seccion: 'Manejo del Dengue con Signos de Alarma',
      pagina: 24,
      texto_relevante: 'Iniciar hidratación parenteral con cristaloides a 10 ml/kg/hora.'
    },
    retroalimentacion_general: 'El razonamiento demuestra solidez en la sospecha clínica temprana.',
    faithfulness_score: 95.5
  };

  it('no debe renderizar nada si result es nulo o indefinido', () => {
    const { container } = render(<FeedbackCard result={null} studentAnswer="" onReset={() => {}} />);
    expect(container.firstChild).toBeNull();
  });

  it('debe renderizar el puntaje obtenido y el valor máximo', () => {
    render(<FeedbackCard result={mockResult} studentAnswer="Paciente con sospecha de dengue" onReset={() => {}} />);
    expect(screen.getByText('8.5')).toBeInTheDocument();
    expect(screen.getByText(/\/ 10 pts/i)).toBeInTheDocument();
  });

  it('debe listar todos los aciertos normativos identificados', () => {
    render(<FeedbackCard result={mockResult} studentAnswer="Paciente con sospecha de dengue" onReset={() => {}} />);
    expect(screen.getByText(/Identificación correcta de signos de alarma/i)).toBeInTheDocument();
    expect(screen.getByText(/Solicitud adecuada de biometría hemática/i)).toBeInTheDocument();
  });

  it('debe listar las omisiones formativas y oportunidades de mejora', () => {
    render(<FeedbackCard result={mockResult} studentAnswer="Paciente con sospecha de dengue" onReset={() => {}} />);
    expect(screen.getByText(/Omisión de esquema de reposición hídrica/i)).toBeInTheDocument();
  });

  it('debe presentar la cita normativa oficial de la GPC del MSP', () => {
    render(<FeedbackCard result={mockResult} studentAnswer="Paciente con sospecha de dengue" onReset={() => {}} />);
    expect(screen.getByText(/Guía de Práctica Clínica Dengue/i)).toBeInTheDocument();
    expect(screen.getByText(/Manejo del Dengue con Signos de Alarma/i)).toBeInTheDocument();
    expect(screen.getByText(/Pág\. 24/i)).toBeInTheDocument();
  });

  it('debe cumplir la regla de oro de diseño: CERO EMOJIS en su contenido', () => {
    const { container } = render(<FeedbackCard result={mockResult} studentAnswer="Paciente con sospecha de dengue" onReset={() => {}} />);
    const textContent = container.textContent || '';
    // Regex para detectar emojis unicode
    const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u;
    expect(emojiRegex.test(textContent)).toBe(false);
  });

  it('debe renderizar la insignia de telemetría de inferencia clínica sin emojis', () => {
    const telemetryResult = {
      ...mockResult,
      llm_latency_ms: 1250,
      llm_model_used: 'Gemini 3.8 Flash',
      paraclinical_studies_count: 2,
      faithfulness_score: 0.95
    };
    render(<FeedbackCard result={telemetryResult} studentAnswer="Test" onReset={() => {}} />);
    expect(screen.getByText(/Telemetría de Inferencia:/i)).toBeInTheDocument();
    expect(screen.getByText(/Gemini 3.8 Flash/i)).toBeInTheDocument();
    expect(screen.getByText(/en 1.25s/i)).toBeInTheDocument();
    expect(screen.getByText(/2 estudio\(s\) paraclínico\(s\)/i)).toBeInTheDocument();
  });

  it('debe renderizar retroalimentacion_general formateada con Markdown estructural', () => {
    const mdResult = {
      ...mockResult,
      retroalimentacion_general: '## Plan Terapéutico\nIniciar infusión de **Sulfato de Magnesio**.'
    };
    render(<FeedbackCard result={mdResult} studentAnswer="Test" onReset={() => {}} />);
    expect(screen.getByRole('heading', { level: 2, name: /Plan Terapéutico/i })).toBeInTheDocument();
    expect(screen.getByText('Sulfato de Magnesio').tagName.toLowerCase()).toBe('strong');
  });
});
