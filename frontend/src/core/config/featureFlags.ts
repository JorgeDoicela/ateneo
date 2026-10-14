/**
 * Configuración de Feature Flags de Ateneo+ (Release v1.0.0)
 * Permite gobernar la activación de capacidades experimentales o modulares
 * sin alterar la arquitectura base ni eliminar componentes del sistema.
 */

export const FEATURE_FLAGS = {
  /**
   * Permite que los estudiantes suban estudios diagnósticos adjuntos (ECG, Rx, laboratorios)
   * desde su dispositivo durante la resolución del caso.
   * En la versión 1.0.0 se desactiva por defecto (false) para priorizar la argumentación
   * clínica estructurada (SOAP) y evitar sobrecarga o alucinaciones por adjuntos externos.
   */
  ENABLE_STUDENT_IMAGE_UPLOAD: import.meta.env.VITE_ENABLE_STUDENT_IMAGE_UPLOAD === 'true',
} as const;
