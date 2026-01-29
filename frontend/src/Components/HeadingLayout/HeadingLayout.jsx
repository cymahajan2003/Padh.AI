import './HeadingLayout.css';

function HeadingLayout() {
  return (
    <section className="heading-layout">
      <p className="heading-line-one">You focus.</p>
      
      <div className="heading-line-two">
        <div className="brand-wrapper">
          <span className="brand padh">Padh</span>
          <span className="brand dot">.</span>
          <span className="brand ai">AI</span>
        </div>
        <span className="handles-text">handles the chaos.</span>
      </div>
    </section>
  );
}

export default HeadingLayout;