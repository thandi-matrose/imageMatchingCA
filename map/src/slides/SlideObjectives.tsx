import React from "react";
import { Slide } from "../components/Slide";
import { AnimatePresence, motion } from "framer-motion";
import { highlight } from "../utils/functions";

interface SlideObjectivesProps {
  step?: number;
}

// Step 0 shows the objectives, step 1 replaces them with the research questions.
// Keep each item on one line so JSX doesn't swallow the spaces around highlights.
const OBJECTIVES: React.ReactNode[] = [
  <>
    Map {highlight("SAR backscatter")} to {highlight("discrete CA cell states")}
  </>,
  <>
    Find the best {highlight("CA state space")} for{" "}
    {highlight("multi-temporal SAR")}
  </>,
  <>
    Find the {highlight("neighbourhood radius")} and kernel that{" "}
    {highlight("minimise RMSE")}
  </>,
  <>
    {highlight("Georeference SAR")} using {highlight("mutual information")} from
    aerial matching
  </>,
  <>Make the {highlight("transition rules visible")}</>,
];

const QUESTIONS: React.ReactNode[] = [
  <>
    How can backscatter be {highlight("discretised into states")} that
    correspond to {highlight("aerial reflectance")}?
  </>,
  <>
    What {highlight("state space")} best represents{" "}
    {highlight("multi-temporal SAR")} against a static aerial baseline?
  </>,
  <>
    What {highlight("neighbourhood radius")} reduces the mismatch caused by{" "}
    {highlight("speckle")}?
  </>,
  <>
    Can matching to aerial imagery establish the{" "}
    {highlight("georeferencing of SAR")}?
  </>,
  <>
    Can the local rules be {highlight("visualised")} to explain why cells are
    classified together?
  </>,
  <>
    How can {highlight("temporal evolution")} show registration being refined?
  </>,
];

export const SlideObjectives = ({ step = 0 }: SlideObjectivesProps) => {
  const showQuestions = step >= 1;
  const items = showQuestions ? QUESTIONS : OBJECTIVES;
  const prefix = showQuestions ? "RQ" : "";

  return (
    <Slide>
      <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
        <h2
          className="section-title"
          style={{ flex: "none", marginBottom: "1rem" }}
        >
          {showQuestions ? "Research Questions" : "Objectives"}
        </h2>

        <AnimatePresence mode="wait">
          <motion.div
            key={showQuestions ? "questions" : "objectives"}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            style={{
              flex: 1,
              minHeight: 0,
              display: "grid",
              gridTemplateRows: `repeat(${items.length}, 1fr)`,
            }}
          >
            {items.map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
                style={{
                  display: "grid",
                  gridTemplateColumns: "6rem 1fr",
                  alignItems: "center",
                  borderBottom:
                    i < items.length - 1 ? "1px solid var(--border)" : "none",
                }}
              >
                <span
                  style={{
                    color: "var(--accent)",
                    fontFamily: "var(--header-font)",
                    fontSize: "clamp(1.1rem, 2.6vh, 1.8rem)",
                  }}
                >
                  {prefix}
                  {i + 1}
                </span>
                <p
                  style={{
                    margin: 0,
                    fontSize: "clamp(1.1rem, 2.8vh, 2rem)",
                    lineHeight: 1.4,
                  }}
                >
                  {item}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>
    </Slide>
  );
};
