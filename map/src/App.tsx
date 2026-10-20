import React, { useRef, useState, useEffect } from "react";
import "./App.css";
import { usePresenterClicker } from "./hooks/usePresenterClicker";

// Import all slide components
import { SlidePoem } from "./slides/SlidePoem";
import { SlideTitle } from "./slides/SlideTitle";
import { SlideMap } from "./slides/SlideMap";
import { SlideTheory } from "./slides/SlideTheory";
import { SlideSignatures } from "./slides/SlideSignatures";
import { SlideResults } from "./slides/SlideResults";
import { SlideMethodology } from "./slides/SlideMethodology";
import { SlideAdditional } from "./slides/SlideAdditional";
import { SlideDemonstration } from "./slides/SlideDemonstration"; // NEW IMPORT
import { SlideContact } from "./slides/SlideContact";

const SLIDES = [
  { Component: SlidePoem, maxSteps: 0 },
  { Component: SlideTitle, maxSteps: 0 },
  { Component: SlideMap, maxSteps: 0 },
  { Component: SlideTheory, maxSteps: 2 },
  { Component: SlideSignatures, maxSteps: 4 },
  { Component: SlideResults, maxSteps: 0 },
  { Component: SlideMethodology, maxSteps: 0 },
  { Component: SlideDemonstration, maxSteps: 4 },
  { Component: SlideContact, maxSteps: 0 },

  { Component: SlideAdditional, maxSteps: 3 },
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

      <div className="slide-indicator">
        {currentSlideIndex + 1} / {TOTAL_SLIDES}
        {SLIDES[currentSlideIndex].maxSteps > 0 &&
          ` (Step ${slideSteps[currentSlideIndex] || 0}/${SLIDES[currentSlideIndex].maxSteps})`}
      </div>
    </>
  );
}

export default App;
