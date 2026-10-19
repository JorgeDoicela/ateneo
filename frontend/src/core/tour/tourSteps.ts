export interface TourStep {
  id: string;
  targetSelector: string;
  title: string;
  description: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
}

export const CATALOG_TOUR_STEPS: TourStep[] = [
  {
    id: 'search',
    targetSelector: '[data-tour="global-search"]',
    title: 'Buscador Normativo Clínico',
    description: 'Encuentra casos clínicos al instante buscando por patología, sintomatología, fármacos o normativa ministerial. Puedes invocarlo rápidamente con el atajo Ctrl + K.',
    placement: 'bottom',
  },
  {
    id: 'adaptive',
    targetSelector: '[data-tour="adaptive-case"]',
    title: 'Caso Recomendado por IA (ZDP)',
    description: 'El motor psicométrico analiza tu historial y selecciona el caso clínico exacto en tu Zona de Desarrollo Próximo para fortalecer tus competencias médicas más débiles.',
    placement: 'bottom',
  },
  {
    id: 'filters',
    targetSelector: '[data-tour="specialty-filters"]',
    title: 'Filtros Curriculares por Especialidad',
    description: 'Segmenta el catálogo según tu rotación clínica actual: Ginecología, Pediatría, Medicina Interna o Urgencias, basadas en las GPC de Ecuador.',
    placement: 'bottom',
  },
  {
    id: 'case-card',
    targetSelector: '[data-tour="case-card"]',
    title: 'Simulación y Código Rojo',
    description: 'Cada ficha muestra la GPC ministerial que rige el caso, su complejidad y si clasifica como Código Rojo de emergencia. Pulsa para iniciar la simulación diagnóstica.',
    placement: 'top',
  },
  {
    id: 'analytics',
    targetSelector: '[data-tour="analytics-nav"]',
    title: 'Mi Desempeño y Radar Clínico',
    description: 'Consulta tu evolución longitudinal y tu radar formativo estructurado en 4 ejes: Diagnóstico, Tratamiento, Prevención y Seguimiento.',
    placement: 'bottom',
  },
  {
    id: 'career',
    targetSelector: '[data-tour="career-nav"]',
    title: 'Carrera Formativa y Puntos XP',
    description: 'Gana puntos de experiencia clínica (XP) por apego a protocolos diagnósticos y asciende de rango desde Estudiante Inicial hasta Residente Clínico de Honor.',
    placement: 'bottom',
  },
  {
    id: 'join-room',
    targetSelector: '[data-tour="join-room-nav"]',
    title: 'Ateneo y Sesiones en Equipo',
    description: 'Ingresa con el código de sala proporcionado por tus docentes para debatir y resolver casos clínicos en equipo de forma sincrónica.',
    placement: 'bottom',
  },
];
