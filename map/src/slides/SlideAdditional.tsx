import React, { useEffect } from "react";
import { Slide } from "../components/Slide";
import { motion, useAnimation } from "framer-motion";

interface SlideAdditionalProps {
  step?: number;
  setStep?: (step: number) => void;
}

const DIAGRAMS = [
  {
    section: "Neighbourhood",
    title: "IDW: High Density",
    src: "/results/heatmaps/Heatmap_of_High Density Urban.png",
    caption:
      "Inverse Distance Weighting evidence propagating through dense urban fabric.",
  },
  {
    section: "Neighbourhood",
    title: "IDW: Water",
    src: "/results/heatmaps/Heatmap_of_Water.png",
    caption:
      "Fragmented neighbourhood evidence corresponding to the irregular shapes of water bodies.",
  },
  {
    section: "Results",
    title: "Confusion Matrix",
    src: "/results/confusion_matrix.png",
    caption:
      "Per-class accuracy showing confusion primarily between urban density classes.",
  },
  {
    section: "Results",
    title: "Convergence",
    src: "/results/convergence_curve.png",
    caption:
      "Number of cells classified per generation across the study area tiles.",
  },
];

export const SlideAdditional = ({
  step = 0,
  setStep,
}: SlideAdditionalProps) => {
  const controls = useAnimation();

  // Animate the horizontal slide whenever the step changes
  useEffect(() => {
    controls.start({
      x: `-${step * 100}%`,
      transition: { duration: 0.6, ease: [0.32, 0.72, 0, 1] },
    });
  }, [step, controls]);

  return (
    <Slide>
      <div className="additional-layout">
        {/* Sidebar Menu */}
        <div className="diagram-menu">
          <p className="menu-header">Sections</p>
          {DIAGRAMS.map((diagram, i) => (
            <button
              key={i}
              onClick={() => setStep && setStep(i)}
              className={`menu-item ${step === i ? "active" : ""}`}
            >
              <span className="menu-section">{diagram.section}</span>
              <span className="menu-title">{diagram.title}</span>
            </button>
          ))}
        </div>

        {/* Horizontal Carousel */}
        <div className="horizontal-carousel-container">
          <motion.div className="horizontal-track" animate={controls}>
            {DIAGRAMS.map((diagram, i) => (
              <div key={i} className="horizontal-slide">
                <div className="diagram-image-wrapper">
                  <img src={diagram.src} alt={diagram.title} />
                </div>
                <div className="diagram-caption">
                  <h3>{diagram.title}</h3>
                  <p>{diagram.caption}</p>
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </Slide>
  );
};
