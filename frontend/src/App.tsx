import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthPage } from './pages/AuthPage';
import { SearchPage } from './pages/SearchPage';
import { DocumentPage } from './pages/DocumentPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { WorkspacePage } from './pages/WorkspacePage';
import { AppLayout } from './components/layout/AppLayout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/auth" element={<AuthPage />} />

        {/* Protected routes — wrapped in AppLayout */}
        <Route element={<AppLayout />}>
          <Route path="/search" element={<SearchPage />} />
          <Route path="/documents/:id" element={<DocumentPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/workspace" element={<WorkspacePage />} />
        </Route>

        {/* Fallback redirect */}
        <Route path="*" element={<Navigate to="/search" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

