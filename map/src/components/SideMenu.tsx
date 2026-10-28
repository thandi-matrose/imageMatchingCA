import React from "react";

interface SlideInfo {
  title?: string;
  maxSteps: number;
}

interface SideMenuProps {
  slides: SlideInfo[];
  currentIndex: number;
  onSelect: (index: number) => void;
}

export const SideMenu: React.FC<SideMenuProps> = ({
  slides,
  currentIndex,
  onSelect,
}) => {
  return (
    <nav className="side-menu">
      <div className="side-menu-track">
        {slides.map((slide, index) => (
          <button
            key={index}
            className={`side-menu-item ${index === currentIndex ? "active" : ""}`}
            onClick={() => onSelect(index)}
            aria-label={`Go to ${slide.title || `Slide ${index + 1}`}`}
          >
            <span className="side-menu-label">
              {slide.title || `Slide ${index + 1}`}
            </span>
          </button>
        ))}
      </div>
    </nav>
  );
};
