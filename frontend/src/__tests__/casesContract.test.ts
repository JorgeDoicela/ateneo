import { describe, it, expect } from 'vitest';
import { ClinicalCasesListSchema, ClinicalCaseSchema } from '../core/validation/schemas';

describe('Contrato clínico de Casos (Resiliencia Zod)', () => {
  it('valida casos con campos nulos en BD sin emitir excepciones de esquema', () => {
    const rawCase = {
      id: "case_test_dinamico_01",
      guia_asociada: "gpc_asma_2019",
      titulo: "Crisis Asmática Severa en Adulto Joven",
      enunciado: "Paciente de 24 años con disnea súbita y taquipnea.",
      pregunta: "¿Cuál es la conducta inicial según la GPC?",
      imagen_url: null,
      nivel_esperado: "pregrado_avanzado",
      fragmento_gpc_ideal_id: null,
      modo_simulacion: "single_turn",
      fases: [],
      competencias_activadas: null,
      tenant_id: "tenant_default",
      activo: true
    };

    const parsedSingle = ClinicalCaseSchema.safeParse(rawCase);
    expect(parsedSingle.success).toBe(true);

    const parsedList = ClinicalCasesListSchema.safeParse([rawCase]);
    expect(parsedList.success).toBe(true);
  });
});
