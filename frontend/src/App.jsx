import { useState } from 'react';
import Header from './Components/Header/Header';
import HeadingLayout from './Components/HeadingLayout/HeadingLayout';
import MainLayout from './Components/MainLayout/MainLayout';
import Footer from './Components/Footer/Footer';
import SummaryPage from './pages/SummaryPage';
import RecommendedPage from './pages/RecommendedPage';
import QuizPage from './pages/QuizPage';
import AssistantPage from './pages/AssistantPage';
import AuthPage from './pages/AuthPage';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem("token")
  );

  const [currentView, setCurrentView] = useState('home');

  const handleNavigate = (view) => {
    setCurrentView(view);
  };

  const handleBack = () => {
    setCurrentView('home');
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    setIsLoggedIn(false);
  };

  const renderContent = () => {
    switch(currentView) {
      case 'home':
        return (
          <>
            <HeadingLayout />
            <MainLayout onNavigate={handleNavigate} />
            <Footer />
          </>
        );
      case 'summary':
        return <SummaryPage onBack={handleBack} />;
      case 'recommended':
        return <RecommendedPage onBack={handleBack} />;
      case 'quiz':
        return <QuizPage onBack={handleBack} />;
      case 'assistant':
        return <AssistantPage onBack={handleBack} />;
      default:
        return null;
    }
  };

  // 🔥 AUTH GATE
  if (!isLoggedIn) {
    return <AuthPage onSuccess={() => setIsLoggedIn(true)} />;
  }

  return (
    <>
      <Header 
        onNavigate={handleNavigate} 
        currentView={currentView}
        onLogout={handleLogout} // optional for later
      />
      {renderContent()}
    </>
  );
}

export default App;