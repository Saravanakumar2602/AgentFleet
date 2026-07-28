import { HashRouter as Router, Routes, Route } from "react-router-dom";
import { PageWrapper } from "./app/components/layout/PageWrapper";
import { Dashboard } from "./app/pages/Dashboard/Dashboard";
import { Fleet } from "./app/pages/Fleet/Fleet";
import { Analytics } from "./app/pages/Analytics/Analytics";
import { Chat } from "./app/pages/Chat/Chat";
import { Workflow } from "./app/pages/Workflow/Workflow";
import { Settings } from "./app/pages/Settings/Settings";
import "./index.css";

function App() {
  return (
    <Router>
      <PageWrapper>
        <Routes>
          <Route path="/"          element={<Dashboard />} />
          <Route path="/fleet"     element={<Fleet />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/workflow"  element={<Workflow />} />
          <Route path="/chat"      element={<Chat />} />
          <Route path="/settings"  element={<Settings />} />
          <Route path="*"          element={<Dashboard />} />
        </Routes>
      </PageWrapper>
    </Router>
  );
}

export default App;
