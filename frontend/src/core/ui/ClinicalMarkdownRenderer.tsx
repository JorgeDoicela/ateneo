import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Components } from 'react-markdown';

export interface ClinicalMarkdownRendererProps {
  content?: string | null;
  className?: string;
  compact?: boolean;
}

/**
 * Renderizador de Markdown clínico basado en compilación AST oficial (react-markdown + remark-gfm).
 * Cumple con los estándares de Ateneo+:
 * - Cero emojis y estética médica sobria (Material 3 Canvas / Slate Tokens).
 * - Tablas clínicas responsivas con scroll horizontal para escalas, dosis y comparativas.
 * - Citas en bloque estilizadas para referencias a Guías de Práctica Clínica (GPC Ecuador).
 * - Fórmulas y valores numéricos monoespaciados legibles.
 */
export const ClinicalMarkdownRenderer: React.FC<ClinicalMarkdownRendererProps> = ({
  content,
  className = '',
  compact = false,
}) => {
  if (!content || typeof content !== 'string' || content.trim().length === 0) {
    return null;
  }

  const customComponents: Components = {
    h1: ({ children }) => (
      <h1 className={`${compact ? 'text-sm' : 'text-base sm:text-lg'} font-bold text-slate-900 tracking-tight mt-3 mb-2 first:mt-0`}>
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className={`${compact ? 'text-xs font-bold' : 'text-sm sm:text-base font-semibold'} text-slate-800 tracking-tight mt-3 mb-1.5 first:mt-0`}>
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className={`${compact ? 'text-xs' : 'text-xs sm:text-sm'} font-semibold text-slate-800 mt-2 mb-1 first:mt-0`}>
        {children}
      </h3>
    ),
    p: ({ children }) => (
      <p className={`${compact ? 'text-xs leading-normal' : 'text-xs sm:text-sm leading-relaxed'} text-slate-700 mb-2 last:mb-0`}>
        {children}
      </p>
    ),
    strong: ({ children }) => (
      <strong className="font-semibold text-slate-900">
        {children}
      </strong>
    ),
    em: ({ children }) => (
      <em className="italic text-slate-800">
        {children}
      </em>
    ),
    ul: ({ children }) => (
      <ul className={`list-disc list-outside ml-4 sm:ml-5 space-y-1 ${compact ? 'text-xs' : 'text-xs sm:text-sm'} text-slate-700 mb-2`}>
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className={`list-decimal list-outside ml-4 sm:ml-5 space-y-1 ${compact ? 'text-xs' : 'text-xs sm:text-sm'} text-slate-700 mb-2`}>
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="leading-relaxed pl-0.5">
        {children}
      </li>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-3 border-[#0b57d0] bg-white/70 px-3.5 py-2 rounded-r-[12px] my-2 text-xs sm:text-sm text-slate-700 italic border-y-0 border-r-0 shadow-2xs">
        {children}
      </blockquote>
    ),
    table: ({ children }) => (
      <div className="overflow-x-auto my-3 rounded-[14px] border border-slate-200/80 bg-white shadow-2xs">
        <table className="w-full text-left border-collapse text-xs">
          {children}
        </table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className="bg-slate-50/90 border-b border-slate-200 text-slate-700">
        {children}
      </thead>
    ),
    tbody: ({ children }) => (
      <tbody className="divide-y divide-slate-100 bg-white text-slate-700">
        {children}
      </tbody>
    ),
    tr: ({ children }) => (
      <tr className="hover:bg-slate-50/50 transition-colors">
        {children}
      </tr>
    ),
    th: ({ children }) => (
      <th className="py-2 px-3 font-semibold text-slate-800 text-[11px] uppercase tracking-wider">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="py-2 px-3 text-slate-700 align-top">
        {children}
      </td>
    ),
    code: ({ children, className: codeClassName }) => {
      const isInline = !codeClassName || !codeClassName.includes('language-');
      if (isInline) {
        return (
          <code className="font-mono text-[11px] sm:text-xs bg-slate-100/90 text-slate-800 px-1.5 py-0.5 rounded-[6px] border border-slate-200/70">
            {children}
          </code>
        );
      }
      return (
        <pre className="font-mono text-xs bg-slate-900 text-slate-100 p-3 rounded-[14px] overflow-x-auto my-2 border border-slate-800">
          <code>{children}</code>
        </pre>
      );
    },
    a: ({ href, children }) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-[#0b57d0] underline underline-offset-2 hover:text-[#0842a0] transition-colors font-medium"
      >
        {children}
      </a>
    ),
    input: ({ type, checked, disabled }) => {
      if (type === 'checkbox') {
        return (
          <input
            type="checkbox"
            checked={checked}
            disabled={disabled}
            readOnly
            className="rounded text-[#0b57d0] focus:ring-0 mr-1.5 align-middle accent-[#0b57d0]"
          />
        );
      }
      return null;
    },
    hr: () => <hr className="my-3 border-slate-200/80" />,
  };

  return (
    <div className={`clinical-markdown leading-relaxed ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={customComponents}>
        {content}
      </ReactMarkdown>
    </div>
  );
};
