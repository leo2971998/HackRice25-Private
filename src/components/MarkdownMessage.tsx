import Markdown from 'react-markdown';

interface MarkdownMessageProps {
  content: string;
  className?: string;
}

export default function MarkdownMessage({ content, className = "" }: MarkdownMessageProps) {
  return (
    <div className={className}>
      <Markdown
        components={{
          // Style headings
          h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-bold mb-2">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-bold mb-1">{children}</h3>,
          
          // Style paragraphs
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          
          // Style lists
          ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="text-sm">{children}</li>,
          
          // Style inline formatting
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          
          // Style code
          code: ({ children }) => (
            <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono">{children}</code>
          ),
          
          // Style links (make them safe and styled)
          a: ({ href, children }) => (
            <a 
              href={href} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </Markdown>
    </div>
  );
}