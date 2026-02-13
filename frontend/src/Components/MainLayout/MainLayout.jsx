import React from "react";
import "./MainLayout.css";
import QuickActions from "../QuickActions/QuickActions";
import RecentDocuments from "../RecentDocuments/RecentDocuments";
import Design from "../Design/Design";

function MainLayout() {
  return (
    <div className="main-layout-wrapper">
      <div className="main-layout-container">
        {/* LEFT SIDE - Quick Actions */}
        <div className="left-panel">
          <QuickActions />
        </div>

        {/* RIGHT SIDE - Design + Recent Documents */}
        <div className="right-panel">
          <div className="right-content">
            <div className="design-container">
              <Design />
            </div>
            <div className="recent-docs-container">
              <RecentDocuments />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MainLayout;