/** [[Note title]] and [[Note title|label]] links, Obsidian-style. */
const WIKI = /\[\[([^\]|\n]+)(?:\|([^\]\n]+))?\]\]/g;

export function wikiTargets(content: string): string[] {
  const seen = new Set<string>();
  for (const m of content.matchAll(WIKI)) seen.add(m[1].trim());
  return [...seen];
}

/** Rewrite wiki links into markdown links with a `wiki:` URL the renderer resolves. */
export function wikiToMarkdown(content: string): string {
  return content.replace(WIKI, (_, title: string, label?: string) =>
    `[${(label ?? title).trim()}](wiki:${encodeURIComponent(title.trim())})`);
}

export const sameTitle = (a: string, b: string) => a.trim().toLowerCase() === b.trim().toLowerCase();

export function linksTo(content: string, title: string): boolean {
  return wikiTargets(content).some(t => sameTitle(t, title));
}
