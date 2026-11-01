import Markdown, { defaultUrlTransform } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Link } from 'react-router-dom';
import { sameTitle, wikiToMarkdown } from '../utils/wiki';
import type { Note } from '../types';

interface Props {
  content: string;
  notes: Note[];
  onMissing?: (title: string) => void;
}

export default function MarkdownView({ content, notes, onMissing }: Props) {
  return (
    <div className="prose-note">
      <Markdown
        remarkPlugins={[remarkGfm]}
        urlTransform={url => (url.startsWith('wiki:') ? url : defaultUrlTransform(url))}
        components={{
          a({ href = '', children }) {
            if (!href.startsWith('wiki:')) return <a href={href} target="_blank" rel="noreferrer">{children}</a>;
            const title = decodeURIComponent(href.slice(5));
            const target = notes.find(n => sameTitle(n.title, title));
            if (target) return <Link to={`/notes/${target.id}`}>{children}</Link>;
            return (
              <a href="#" className="missing" title={`No note called "${title}" yet — click to create it`}
                onClick={e => { e.preventDefault(); onMissing?.(title); }}>{children}</a>
            );
          },
        }}
      >
        {wikiToMarkdown(content)}
      </Markdown>
    </div>
  );
}
