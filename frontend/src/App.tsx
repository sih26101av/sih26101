/**
 * FILE: src/App.tsx
 */

import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LearnerDashboard from "./pages/LearnerDashboard";
import { ThemeProvider } from "./hooks/useTheme";

// EMP-8472 matches the live FastAPI backend user ID
const ACTIVE_OFFICIAL_ID = "EMP-8472";

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to={`/dashboard/${ACTIVE_OFFICIAL_ID}`} replace />} />
          <Route
            path="/dashboard/:officialId"
            element={<LearnerDashboard officialId={ACTIVE_OFFICIAL_ID} />}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;