import { Slide } from "../components/Slide";
import { motion, AnimatePresence } from "framer-motion";
import { highlight } from "../utils/functions";

interface SlideGrowthResultsProps {
  step?: number;
}

export const SlideGrowthResults = ({ step = 0 }: SlideGrowthResultsProps) => {
  return (
    <Slide>
      <h2 className="section-title">Results of Growth</h2>

      <div className="two-three-col" style={{ width: "80%" }}>
        {/* Left Column: Dynamic Text */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            minHeight: "300px",
          }}
        >
          <AnimatePresence mode="wait">
            {step === 0 && (
              <motion.div
                key="step0"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                <h3 style={{ color: "var(--accent)", marginBottom: "1rem" }}>
                  Tuning the CA Parameters
                </h3>
                <p>
                  <strong>{highlight("Neighbourhood Window")}:</strong> A 3×3
                  Moore neighbourhood was chosen. Larger windows smoothed the
                  results too aggressively, erasing fine urban features like
                  narrow roads.
                </p>
                <p>
                  <strong>{highlight("Time to Terminal Velocity")}:</strong>{" "}
                  Controls how quickly we trust the neighbourhood over the
                  pixel's own features. Setting this too low caused the
                  algorithm to "flood" the map before pixels could be evaluated
                  locally.
                </p>
                <p>
                  <strong>{highlight("Alpha")}:</strong> The balance parameter.
                  The quadratic scaling ensures early growth is based on strong
                  features, transitioning to neighbourhood context in later
                  generations.
                </p>
              </motion.div>
            )}

            {step === 1 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                <h3 style={{ color: "var(--accent)", marginBottom: "1rem" }}>
                  Comparison with Baselines
                </h3>
                <p>
                  <strong>
                    vs GrowCut (<code>gc_</code>):
                  </strong>{" "}
                  GrowCut grows rapidly but lacks our fuzzy feature weighting.
                  It struggles to separate highly overlapping urban density
                  classes.
                </p>
                <p>
                  <strong>
                    vs Random Forest (<code>rf_</code>):
                  </strong>{" "}
                  The RF is highly sensitive to individual pixel colours.
                  syCAMOR uses the CA to enforce spatial connectivity, removing
                  the typical RF "speckle" effect.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right Column: Dynamic Images */}
        <div
          className="image-container"
          style={{
            position: "relative",
            minHeight: "400px",
          }}
        >
          <AnimatePresence mode="wait">
            {step === 0 && (
              <motion.img
                key="img0"
                src="alpha.png" // Replace with your graph of alpha(t)
                alt="Alpha Scaling"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                style={{
                  maxWidth: "100%",
                  maxHeight: "100%",
                  objectFit: "contain",
                  borderRadius: "8px",
                }}
              />
            )}

            {step === 1 && (
              <motion.div
                key="img2"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "1rem",
                  width: "100%",
                  height: "100%",
                }}
              >
                <div style={{ textAlign: "center" }}>
                  <img
                    src="W08A_1_gc.png"
                    alt="GrowCut"
                    style={{ width: "100%", borderRadius: "8px" }}
                  />
                  <p style={{ fontSize: "0.8rem", marginTop: "0.5rem" }}>
                    GrowCut
                  </p>
                </div>
                <div style={{ textAlign: "center" }}>
                  <img
                    src="W08A_1_rf.png"
                    alt="Random Forest"
                    style={{ width: "100%", borderRadius: "8px" }}
                  />
                  <p style={{ fontSize: "0.8rem", marginTop: "0.5rem" }}>
                    Random Forest
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </Slide>
  );
};
