import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Components } from 'react-markdown';

export interface StreamingMarkdownViewerProps {
  content: string;
  isStreaming?: boolean;
}

/**
 * Visor declarativo de texto clínico y markdown fluido para respuestas en streaming y debriefing socrático.
 * Utiliza compilación AST oficial (react-markdown + remark-gfm), cumpliendo la regla innegociable de cero emojis.
 */
export const StreamingMarkdownViewer: React.FC<StreamingMarkdownViewerProps> = ({
  content,
  isStreaming = false,
}) => {
  if (!content && !isStreaming) {
    return null;
  }

  const customComponents: Components = {
    p: ({ children }) => {
      // Extracción recursiva de texto plano para detectar preguntas socráticas
      const textContent = React.Children.toArray(children)
        .map((child) => (typeof child === 'string' ? child : ''))
        .join('');
      const isQuestion = textContent.trim().endsWith('?');

      return (
        <p
          className={
            isQuestion
              ? 'p-3 bg-cyan-50/60 rounded-xl border-l-2 border-cyan-500 text-cyan-950 font-medium my-2'
              : 'text-slate-800 text-sm leading-relaxed mb-2 last:mb-0'
          }
        >
          {children}
        </p>
      );
    },
    ul: ({ children }) => (
      <ul className="list-disc pl-5 space-y-1 text-slate-700 my-2 text-sm">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal pl-5 space-y-1 text-slate-700 my-2 text-sm">
        {children}
      </ol>
    ),
    li: ({ children }) => <li className="leading-relaxed">{children}</li>,
    strong: ({ children }) => <strong className="font-semibold text-slate-900">{children}</strong>,
    em: ({ children }) => <em className="italic text-slate-800">{children}</em>,
    table: ({ children }) => (
      <div className="overflow-x-auto my-3 rounded-[14px] border border-slate-200/80 bg-white">
        <table className="w-full text-left border-collapse text-xs">
          {children}
        </table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-800">
        {children}
      </thead>
    ),
    tbody: ({ children }) => (
      <tbody className="divide-y divide-slate-100 bg-white text-slate-700">
        {children}
      </tbody>
    ),
    th: ({ children }) => <th className="py-2 px-3">{children}</th>,
    td: ({ children }) => <td className="py-2 px-3 align-top">{children}</td>,
    code: ({ children }) => (
      <code className="font-mono text-xs bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded border border-slate-200">
        {children}
      </code>
    ),
  };

  return (
    <div className="streaming-markdown text-slate-800 text-sm leading-relaxed font-normal">
      {content && (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={customComponents}>
          {content}
        </ReactMarkdown>
      )}

      {isStreaming && (
        <span
          data-testid="streaming-cursor"
          className="inline-block w-2 h-4 ml-1 bg-cyan-600 animate-pulse align-middle"
          aria-label="Generando respuesta..."
        />
      )}
    </div>
  );
};

export default StreamingMarkdownViewer;
