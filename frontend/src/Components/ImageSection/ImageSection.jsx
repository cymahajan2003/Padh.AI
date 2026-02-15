import React from 'react';
import './ImageSection.css';

function ImageSection() {
  return (
    <section className="image-section">
      {/* No background circle anymore */}

      <div className="content">
        {/* Optional: Uncomment if you want a section title */}
        {/* <div className="section-title">Featured</div> */}
        
        <div className="images-container">
          <div className="image-container">
            <img 
              src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
              alt="AI-Powered Learning"
              loading="lazy"
            />
            <div className="image-overlay"></div>
            <div className="image-caption">
              <span className="caption-title">AI-Powered Learning</span>
              <span className="caption-description">Personalized education paths adapted to your pace</span>
            </div>
          </div>

          <div className="image-container">
            <img 
              src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
              alt="Reduce Cognitive Load"
              loading="lazy"
            />
            <div className="image-overlay"></div>
            <div className="image-caption">
              <span className="caption-title">Reduce Cognitive Load</span>
              <span className="caption-description">Streamlined information delivery for better retention</span>
            </div>
          </div>

          <div className="image-container">
            <img 
              src="https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
              alt="Efficient Learning"
              loading="lazy"
            />
            <div className="image-overlay"></div>
            <div className="image-caption">
              <span className="caption-title">Efficient Learning</span>
              <span className="caption-description">Master skills faster with optimized study techniques</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default ImageSection;