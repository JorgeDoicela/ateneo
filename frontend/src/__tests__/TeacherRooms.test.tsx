import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent, cleanup } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import TeacherCasesPage from '../modules/teacher/pages/TeacherCasesPage';
import AteneoRoom from '../modules/collaboration/pages/AteneoRoom';
import { useAteneoRoomStore } from '../core/stores/useAteneoRoomStore';

// Mock de AuthContext como docente
const mockTeacher = {
  id: 'usr_docente_001',
  email: 'carlos.andrade@ateneo.edu.ec',
  nombre: 'Dr. Carlos Andrade',
  rol: 'docente' as const
};

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: mockTeacher
  })
}));

// Mock de casesApi
vi.mock('../modules/cases/api/casesApi', () => ({
  default: {
    getCases: vi.fn().mockResolvedValue([
      {
        id: 'case_preeclampsia_01',
        titulo: 'Gestante con Trastorno Hipertensivo y Signos de Severidad',
        enunciado: 'Gestante de 32 semanas acude a urgencias...',
        caso_preambulo: 'Gestante de 32 semanas...',
        guia_asociada: 'MSP_Trastornos-hipertensivos-del-embarazo-con-portada-3.pdf',
        fases: [{ numero: 1 }, { numero: 2 }]
      }
    ])
  }
}));

// Mock de collaborationApi
vi.mock('../modules/collaboration/api/collaborationApi', () => ({
  default: {
    getTeacherRooms: vi.fn().mockResolvedValue([
      {
        room_code: 'ATENEO-8492',
        codigo: 'ATENEO-8492',
        case_id: 'case_preeclampsia_01',
        case_title: 'Gestante con Trastorno Hipertensivo y Signos de Severidad',
        guia_asociada: 'MSP_Trastornos-hipertensivos-del-embarazo-con-portada-3.pdf',
        docente_id: 'usr_docente_001',
        docente_nombre: 'Dr. Carlos Andrade',
        estado: 'resolucion',
        participantes: {
          'alumno1@ateneo.edu.ec': {
            nombre: 'Estudiante María Silva',
            rol: 'alumno',
            respondido: true,
            resultado_evaluacion: {
              score: 9.0,
              score_max: 10,
              aciertos: ['Sulfato de magnesio indicado oportunamente'],
              omisiones: []
            }
          }
        },
        analitica_consenso: {
          promedio_sala: 9.0,
          score_promedio: 9.0,
          total_respondidos: 1,
          total_conectados: 1,
          porcentaje_participacion: 100,
          nivel_consenso: 'Alto Consenso Alineado a la GPC',
          top_brechas_sala: []
        }
      }
    ]),
    getRoom: vi.fn().mockResolvedValue({
      room_code: 'ATENEO-8492',
      codigo: 'ATENEO-8492',
      case_id: 'case_preeclampsia_01',
      case_title: 'Gestante con Trastorno Hipertensivo y Signos de Severidad',
      case_enunciado: 'Gestante de 32 semanas acude a urgencias por cefalea holocraneana...',
      case_pregunta: '¿Cuál es el esquema farmacológico de neuroprotección materna normado?',
      docente_id: 'usr_docente_001',
      docente_nombre: 'Dr. Carlos Andrade',
      estado: 'resolucion',
      participantes: {
        'alumno1@ateneo.edu.ec': {
          email: 'alumno1@ateneo.edu.ec',
          nombre: 'Estudiante María Silva',
          rol: 'alumno',
          respuesta: 'Se indica esquema de Zuspan con Sulfato de Magnesio: 4g IV en 20 minutos como dosis de impregnación.',
          respondido: true,
          resultado_evaluacion: {
            score: 9.5,
            score_max: 10,
            aciertos: ['Esquema de Zuspan correctamente prescrito', 'Dosis de carga 4g IV en 20 min'],
            omisiones: ['Monitoreo estricto del reflejo rotuliano y diuresis horaria'],
            cita_normativa: {
              guia: 'GPC Trastornos Hipertensivos del Embarazo MSP',
              pagina: 24,
              seccion: 'Esquema de Neuroprotección'
            }
          }
        }
      },
      analitica_consenso: {
        promedio_sala: 9.5,
        score_promedio: 9.5,
        total_respondidos: 1,
        total_conectados: 1,
        porcentaje_participacion: 100,
        nivel_consenso: 'Alto Consenso Alineado a la GPC',
        top_brechas_sala: [
          { brecha: 'Monitoreo de reflejos tendinosos profundos', estudiantes_afectados: 1, porcentaje: 100 }
        ]
      }
    }),
    createRoom: vi.fn().mockResolvedValue({
      room_code: 'ATENEO-9999',
      codigo: 'ATENEO-9999',
      case_id: 'case_preeclampsia_01',
      docente_id: 'usr_docente_001',
      estado: 'espera'
    }),
    updateRoomStatus: vi.fn().mockResolvedValue({
      status: 'ok',
      estado: 'discusion'
    }),
    deleteRoom: vi.fn().mockResolvedValue({ status: 'ok' })
  }
}));

describe('Suite de Pruebas: Consola Docente y Gestión de Salas de Ateneo (Ateneo+)', () => {
  beforeEach(() => {
    useAteneoRoomStore.getState().resetRoom();
  });

  afterEach(() => {
    cleanup();
    useAteneoRoomStore.getState().resetRoom();
  });

  describe('Página de Casos y Salas del Docente (TeacherCasesPage)', () => {
    it('debe renderizar la lista de salas activas del docente y el catálogo de casos', async () => {
      render(
        <MemoryRouter>
          <TeacherCasesPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/Salas de Simulación en Vivo/i)).toBeInTheDocument();
        expect(screen.getByText(/ATENEO-8492/i)).toBeInTheDocument();
        expect(screen.getByText(/Catálogo de Casos para Nueva Sala de Ateneo/i)).toBeInTheDocument();
      });

      // Verificar métricas de sala activa
      expect(screen.getByText(/Resolución Activa/i)).toBeInTheDocument();
      expect(screen.getByText(/Entrar a Sala/i)).toBeInTheDocument();
      expect(screen.getByText(/Crear Sala Ateneo/i)).toBeInTheDocument();
    });

    it('permite copiar el código de sala al portapapeles con feedback visual', async () => {
      // Mock de navigator.clipboard
      const writeTextMock = vi.fn().mockResolvedValue(undefined);
      Object.assign(navigator, {
        clipboard: {
          writeText: writeTextMock
        }
      });

      render(
        <MemoryRouter>
          <TeacherCasesPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/ATENEO-8492/i)).toBeInTheDocument();
      });

      const copyBtn = screen.getByTitle(/Copiar código de sala/i);
      fireEvent.click(copyBtn);

      expect(writeTextMock).toHaveBeenCalledWith('ATENEO-8492');
      await waitFor(() => {
        expect(screen.getByText(/Copiado/i)).toBeInTheDocument();
      });
    });

    it('permite al docente abrir modal de configuración, elegir Ateneo en Grupo y crear la sala con esa modalidad', async () => {
      render(
        <MemoryRouter>
          <TeacherCasesPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/Crear Sala Ateneo/i)).toBeInTheDocument();
      });

      // Clic en crear sala abre el modal
      fireEvent.click(screen.getByText(/Crear Sala Ateneo/i));

      await waitFor(() => {
        expect(screen.getByText(/Configuración de Simulación Sincrónica/i)).toBeInTheDocument();
        expect(screen.getByText(/Ateneo en Grupo/i)).toBeInTheDocument();
        expect(screen.getAllByText(/Resolución Individual/i).length).toBeGreaterThan(0);
      });

      // Seleccionar Ateneo en Grupo
      const groupOption = screen.getByText(/Co-escritura en vivo con WebSockets/i);
      fireEvent.click(groupOption);

      // Confirmar creación
      const submitBtn = screen.getByText(/Crear y Abrir Sala/i);
      fireEvent.click(submitBtn);

      await waitFor(() => {
        expect(screen.queryByText(/Configuración de Simulación Sincrónica/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Moderación del Docente dentro de la Sala (AteneoRoom)', () => {
    it('debe renderizar el pipeline de 4 fases y el botón para avanzar a Consenso y Discusión', async () => {
      render(
        <MemoryRouter initialEntries={['/ateneo/ATENEO-8492']}>
          <Routes>
            <Route path="/ateneo/:roomCode" element={<AteneoRoom />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getAllByText(/Abrir Consenso y Discusión/i).length).toBeGreaterThan(0);
      });

      // Verificar que se renderiza el indicador de consenso con los datos calculados
      expect(screen.getAllByText(/Consenso Diagnóstico de la Cohorte/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Alto Consenso Alineado a la GPC/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/9.5/).length).toBeGreaterThan(0);
    });

    it('permite al docente inspeccionar el dictamen clínico y la evaluación RAG de un estudiante', async () => {
      render(
        <MemoryRouter initialEntries={['/ateneo/ATENEO-8492']}>
          <Routes>
            <Route path="/ateneo/:roomCode" element={<AteneoRoom />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/Estudiante María Silva/i)).toBeInTheDocument();
        expect(screen.getByText(/9.5\/10/i)).toBeInTheDocument();
      });

      // Clic para desplegar el inspector de dictamen
      const studentCard = screen.getByText(/Estudiante María Silva/i);
      fireEvent.click(studentCard);

      await waitFor(() => {
        expect(screen.getByText(/Dictamen Clínico Emitido:/i)).toBeInTheDocument();
        expect(screen.getByText(/Se indica esquema de Zuspan con Sulfato de Magnesio/i)).toBeInTheDocument();
        expect(screen.getByText(/Esquema de Zuspan correctamente prescrito/i)).toBeInTheDocument();
        expect(screen.getByText(/Monitoreo estricto del reflejo rotuliano/i)).toBeInTheDocument();
        expect(screen.getByText(/GPC Trastornos Hipertensivos del Embarazo MSP/i)).toBeInTheDocument();
      });
    });
  });
});
