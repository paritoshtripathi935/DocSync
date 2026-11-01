import { AlertTriangle } from 'lucide-react';

export default function ErrorNote({ message }: { message: string }) {
  return (
    <div role="alert" className="flex gap-2.5 rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm">
      <AlertTriangle size={16} className="text-danger shrink-0 mt-0.5" />
      <span className="break-words min-w-0">{message}</span>
    </div>
  );
}
