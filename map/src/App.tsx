import React, { useRef, useState, useEffect } from "react";
import "./App.css";
import { usePresenterClicker } from "./hooks/usePresenterClicker";
import "katex/dist/katex.min.css";
// Components
import { SideMenu } from "./components/SideMenu";

// Slides
import { SlidePoem } from "./slides/SlidePoem";
import { SlideImpact } from "./slides/SlideImpact";
import { SlideTitle } from "./slides/SlideTitle";
import { SlideBackground } from "./slides/SlideBackground";
import { SlideObjectives } from "./slides/SlideObjectives";
import { SlideMap } from "./slides/SlideMap";
import { SlideTheory } from "./slides/SlideTheory";
import { SlideSignatures } from "./slides/SlideSignatures";
import { SlideResults } from "./slides/SlideResults";
import { SlideMethodology } from "./slides/SlideMethodology";
import { SlideGoodbye } from "./slides/SlideGoodbye";
import { SlideContact } from "./slides/SlideContact";
import { SlideGrowthResults } from "./slides/SlideResultOfGrowth";
import { SlideAnalysis } from "./slides/SlideAnalysis";
import { SlideRecommendations } from "./slides/SlideRecommendations";

// Added titles for the side menu
const SLIDES = [
  { Component: SlidePoem, maxSteps: 2, title: "Introduction" },
  { Component: SlideMap, maxSteps: 0, title: "Study Area" },
  { Component: SlideImpact, maxSteps: 2, title: "Impact" },
  { Component: SlideTitle, maxSteps: 0, title: "Title" },
  { Component: SlideBackground, maxSteps: 2, title: "Background" },
  { Component: SlideObjectives, maxSteps: 0, title: "Objectives" },
  { Component: SlideTheory, maxSteps: 0, title: "Theory" }, // Changed to 0
  { Component: SlideMethodology, maxSteps: 4, title: "Methodology" },
  { Component: SlideSignatures, maxSteps: 0, title: "Radar Signatures" },
  { Component: SlideResults, maxSteps: 3, title: "Results" },
  //{ Component: SlideDemonstration, maxSteps: 4, title: "Demo" },

  { Component: SlideGrowthResults, maxSteps: 1, title: "Growth Results" },
  { Component: SlideAnalysis, maxSteps: 0, title: "Analysis" },
  { Component: SlideRecommendations, maxSteps: 0, title: "Recommendations" },

  { Component: SlideGoodbye, maxSteps: 0, title: "Conclusion" },
  { Component: SlideContact, maxSteps: 0, title: "Contact" },
  //{ Component: SlideAdditional, maxSteps: 3, title: "Additional" },
];

function App() {
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [slideSteps, setSlideSteps] = useState<Record<number, number>>({});

  const slideRefs = useRef<(HTMLDivElement | null)[]>([]);
  const TOTAL_SLIDES = SLIDES.length;

  const handleNext = () => {
    const { maxSteps } = SLIDES[currentSlideIndex];
    const currentStep = slideSteps[currentSlideIndex] || 0;

    if (currentStep < maxSteps) {
      setSlideSteps((prev) => ({
        ...prev,
        [currentSlideIndex]: currentStep + 1,
      }));
      return;
    }

    setCurrentSlideIndex((prev) => Math.min(prev + 1, TOTAL_SLIDES - 1));
  };

  const handlePrev = () => {
    const currentStep = slideSteps[currentSlideIndex] || 0;

    if (currentStep > 0) {
      setSlideSteps((prev) => ({
        ...prev,
        [currentSlideIndex]: currentStep - 1,
      }));
      return;
    }

    setCurrentSlideIndex((prev) => Math.max(prev - 1, 0));
  };

  usePresenterClicker({ onNext: handleNext, onPrev: handlePrev });

  useEffect(() => {
    const activeSlide = slideRefs.current[currentSlideIndex];
    if (activeSlide) {
      activeSlide.scrollIntoView({ behavior: "smooth" });
    }
  }, [currentSlideIndex]);

  const updateSlideStep = (index: number, step: number) => {
    setSlideSteps((prev) => ({ ...prev, [index]: step }));
  };

  return (
    <>
      {/* 2. Side Navigation Menu */}
      <SideMenu
        slides={SLIDES}
        currentIndex={currentSlideIndex}
        onSelect={(index) => setCurrentSlideIndex(index)}
      />

      {/* 3. Presentation Content */}
      <div className="presentation-container">
        {SLIDES.map(({ Component }, index) => {
          const SlideComp = Component as React.ComponentType<{
            step?: number;
            setStep?: (step: number) => void;
          }>;

          return (
            <div
              key={index}
              ref={(el) => {
                slideRefs.current[index] = el;
              }}
            >
              <SlideComp
                step={slideSteps[index] || 0}
                setStep={(s) => updateSlideStep(index, s)}
              />
            </div>
          );
        })}
      </div>

      {/* 4. Bottom Right Slide Indicator */}
      <div className="slide-indicator">
        {currentSlideIndex + 1} / {TOTAL_SLIDES}
        {SLIDES[currentSlideIndex].maxSteps > 0 &&
          ` (Step ${slideSteps[currentSlideIndex] || 0}/${SLIDES[currentSlideIndex].maxSteps})`}
      </div>
    </>
  );
}

export default App;
