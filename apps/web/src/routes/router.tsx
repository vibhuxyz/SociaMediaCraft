import { Routes, Route } from 'react-router-dom';
import { PageLayout } from '../components/layout/PageLayout';
import { DashboardPage } from '../features/dashboard/pages/DashboardPage';
import { V0Page } from '../features/dashboard/pages/V0Page';
import { V1Page } from '../features/dashboard/pages/V1Page';
import { V2Page } from '../features/dashboard/pages/V2Page';
import { V3Page } from '../features/dashboard/pages/V3Page';
import { V4Page } from '../features/dashboard/pages/V4Page';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/admin" element={<PageLayout />}>
        <Route index element={<V0Page />} />
        <Route path="v0" element={<V0Page />} />
        <Route path="v1" element={<V1Page />} />
        <Route path="v2" element={<V2Page />} />
        <Route path="v3" element={<V3Page />} />
        <Route path="v4" element={<V4Page />} />
      </Route>
    </Routes>
  );
}
