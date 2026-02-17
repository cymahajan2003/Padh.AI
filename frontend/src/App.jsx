import { useState } from 'react';
import Header from './Components/Header/Header';
import HeadingLayout from './Components/HeadingLayout/HeadingLayout';
import MainLayout from './Components/MainLayout/MainLayout';
import Footer from './Components/Footer/Footer';
import SummaryPage from './pages/SummaryPage';

function App() {
  const [currentView, setCurrentView] = useState('home');

  const handleNavigate = (view) => {
    setCurrentView(view);
  };

  const handleBack = () => {
    setCurrentView('home');
  };

  return (
    <>
      <Header />
      {currentView === 'home' ? (
        <>
          <HeadingLayout />
          <MainLayout onNavigate={handleNavigate} />
        </>
      ) : (
        <SummaryPage onBack={handleBack} />
      )}
      <Footer />
    </>
  );
}

export default App;