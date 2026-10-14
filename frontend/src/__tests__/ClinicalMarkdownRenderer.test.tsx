import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ClinicalMarkdownRenderer } from '../core/ui/ClinicalMarkdownRenderer';

describe('Suite de Pruebas: Renderizador de Markdown Clínico (ClinicalMarkdownRenderer - Ateneo+)', () => {
  it('maneja contenido nulo, indefinido o vacío de forma segura sin romper la interfaz', () => {
    const { container: c1 } = render(<ClinicalMarkdownRenderer content={null} />);
    expect(c1.firstChild).toBeNull();

    const { container: c2 } = render(<ClinicalMarkdownRenderer content="" />);
    expect(c2.firstChild).toBeNull();

    const { container: c3 } = render(<ClinicalMarkdownRenderer content="   " />);
    expect(c3.firstChild).toBeNull();
  });

  it('renderiza encabezados clínicos h1, h2 y h3 con jerarquía adecuada', () => {
    const markdown = `
# Evaluación Diagnóstica
## Conducta Terapéutica Inmediata
### Parámetros de Monitoreo Fetal
`;
    render(<ClinicalMarkdownRenderer content={markdown} />);

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Evaluación Diagnóstica');
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Conducta Terapéutica Inmediata');
    expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Parámetros de Monitoreo Fetal');
  });

  it('renderiza listas ordenadas y con viñetas para algoritmos clínicos', () => {
    const markdown = `
1. Asegurar vía aérea permeable
2. Canalizar dos vías periféricas
3. Administrar dosis de impregnación

- Presión arterial sistólica >= 160 mmHg
- Proteinuria positiva
`;
    render(<ClinicalMarkdownRenderer content={markdown} />);

    expect(screen.getByText('Asegurar vía aérea permeable')).toBeInTheDocument();
    expect(screen.getByText('Canalizar dos vías periféricas')).toBeInTheDocument();
    expect(screen.getByText('Presión arterial sistólica >= 160 mmHg')).toBeInTheDocument();
  });

  it('renderiza tablas de dosificación y escalas clínicas de forma responsiva mediante remark-gfm', () => {
    const markdown = `
| Fármaco | Dosis Inicial | Vía | Frecuencia |
| :--- | :--- | :--- | :--- |
| Sulfato de Magnesio | 4 g en 20 min | IV | Impregnación |
| Nifedipino | 10 mg | VO | Cada 20 min |
`;
    render(<ClinicalMarkdownRenderer content={markdown} />);

    // Verificación de cabeceras de tabla
    expect(screen.getByText('Fármaco')).toBeInTheDocument();
    expect(screen.getByText('Dosis Inicial')).toBeInTheDocument();
    expect(screen.getByText('Vía')).toBeInTheDocument();

    // Verificación de celdas de fármacos clínicos
    expect(screen.getByText('Sulfato de Magnesio')).toBeInTheDocument();
    expect(screen.getByText('4 g en 20 min')).toBeInTheDocument();
    expect(screen.getByText('Nifedipino')).toBeInTheDocument();
    expect(screen.getByText('10 mg')).toBeInTheDocument();
  });

  it('renderiza citas en bloque para referencias normativas de GPC Ecuador', () => {
    const markdown = `
> GPC Trastornos Hipertensivos del Embarazo, MSP Ecuador, pág. 40.
`;
    render(<ClinicalMarkdownRenderer content={markdown} />);

    const quote = screen.getByText(/GPC Trastornos Hipertensivos del Embarazo, MSP Ecuador/i);
    expect(quote).toBeInTheDocument();
  });

  it('renderiza fórmulas clínicas y valores monoespaciados', () => {
    const markdown = `
Calcular el aclaramiento mediante la fórmula \`CrCl = ((140 - edad) * peso) / (72 * CrS)\`.
`;
    render(<ClinicalMarkdownRenderer content={markdown} />);

    const inlineCode = screen.getByText('CrCl = ((140 - edad) * peso) / (72 * CrS)');
    expect(inlineCode).toBeInTheDocument();
    expect(inlineCode.tagName.toLowerCase()).toBe('code');
  });

  it('cumple con el estándar innegociable de cero emojis en el árbol del renderizador', () => {
    const markdown = `
**Dictamen Formativo:**
Se confirma el diagnóstico clínico sin anomalías.
`;
    const { container } = render(<ClinicalMarkdownRenderer content={markdown} />);
    const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u;
    expect(emojiRegex.test(container.textContent || '')).toBe(false);
  });

  it('renderiza enlaces clínicos de forma segura con target blank y rel noopener noreferrer', () => {
    const markdown = `
Consultar el [Protocolo Oficial GPC](https://salud.gob.ec/gpc-preeclampsia) para más detalles.
`;
    render(<ClinicalMarkdownRenderer content={markdown} />);

    const link = screen.getByRole('link', { name: 'Protocolo Oficial GPC' });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://salud.gob.ec/gpc-preeclampsia');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('renderiza listas de tareas de GFM con checkboxes de sólo lectura', () => {
    const markdown = `
- [x] Vía aérea asegurada
- [ ] Administración de labetalol
`;
    render(<ClinicalMarkdownRenderer content={markdown} />);

    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes).toHaveLength(2);
    expect(checkboxes[0]).toBeChecked();
    expect(checkboxes[1]).not.toBeChecked();
  });
});
