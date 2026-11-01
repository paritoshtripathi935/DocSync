/**
 *   /             Workspace home — recent notes, create one
 *   /notes/:id    Editor with backlinks, links and version history
 */
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import HomePage from './pages/HomePage';
import NotePage from './pages/NotePage';
import { NotesProvider } from './state/NotesContext';

export default function AuthedApp() {
  return (
    <BrowserRouter>
      <NotesProvider>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<HomePage />} />
            <Route path="notes/:noteId" element={<NotePage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </NotesProvider>
    </BrowserRouter>
  );
}
