import { Slide } from "../components/Slide";
import { InlineMath } from "react-katex";
import { motion, AnimatePresence } from "framer-motion";

interface SlideResultsProps {
  step?: number;
}

export const SlideResults = ({ step = 0 }: SlideResultsProps) => {
  // Combined array for images and corresponding text
  const carouselItems = [
    {
      src: "/figures/W08A_1_radar.png",
      alt: "Radar Input",
      title: "1. Raw SAR Input",
      description: (
        <p>
          The pre-processed Sentinel-1 radar imagery serves as the foundation.
          Unlike optical imagery, it penetrates cloud cover and captures the
          structural geometry of the urban fabric.
        </p>
      ),
    },
    {
      src: "/figures/seed.gif", // Assuming this might be a static image or gif
      alt: "Seed Classification",
      title: "2. Seeding Outcomes",
      description: (
        <>
          <p>
            A membership threshold of <InlineMath math="\tau_{seed} = 0.80" />{" "}
            seeded 31,881 of the 1.06 million cells.
          </p>
          <p>
            This is just <strong>3.02% of the study area</strong>, leaving the
            vast majority unclassified to be resolved by the CA.
          </p>
        </>
      ),
    },
    {
      src: "/figures/frame.gif",
      alt: "Region Growing Animation",
      title: "3. Iterative Region Growing",
      description: (
        <p>
          The CA expands these seeds iteratively using the Inverse Distance
          Weighting (IDW) neighbourhood rule. Watch as the unclassified pixels
          are absorbed into the surrounding urban classes.
        </p>
      ),
    },
    {
      src: "/figures/W08A_1_WATER.png", // Note: Added .png assuming it was a typo in original
      alt: "Neighbourhood Heatmap",
      title: "4. Neighbourhood Evidence",
      description: (
        <p>
          The IDW heatmap for the Water class. The distance-decayed convolution
          shows how evidence propagates spatially from the seeds across the tile
          at each time step.
        </p>
      ),
    },
  ];

  // Ensure step doesn't go out of bounds if maxSteps isn't set perfectly
  const safeStep = Math.min(step, carouselItems.length - 1);
  const activeItem = carouselItems[safeStep];

  return (
    <Slide>
      <h2 className="section-title">Classification Results</h2>

      <div className="two-col" style={{ alignItems: "center" }}>
        {/* Left Column: The Carousel */}
        <div
          className="carousel-container"
          style={{
            height: "60vh",
            position: "relative",
            overflow: "hidden",
            borderRadius: "12px",
            background: "#f8f9fa",
          }}
        >
          <motion.div
            style={{ display: "flex", width: "100%", height: "100%" }}
            animate={{ x: `-${safeStep * 100}%` }}
            transition={{ duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
          >
            {carouselItems.map((item, index) => (
              <div
                key={index}
                style={{
                  height: "100%",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  padding: "1rem",
                }}
              >
                <img
                  src={item.src}
                  alt={item.alt}
                  style={{
                    maxWidth: "100%",
                    maxHeight: "100%",
                    objectFit: "contain",
                    borderRadius: "8px",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  }}
                />
              </div>
            ))}
          </motion.div>

          {/* Progress Dots */}
          <div
            style={{
              position: "absolute",
              bottom: "1rem",
              width: "100%",
              display: "flex",
              justifyContent: "center",
              gap: "0.5rem",
            }}
          >
            {carouselItems.map((_, idx) => (
              <div
                key={idx}
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  backgroundColor:
                    idx === safeStep ? "var(--accent)" : "rgba(0,0,0,0.2)",
                  transition: "background-color 0.3s",
                }}
              />
            ))}
          </div>
        </div>

        {/* Right Column: Dynamic Text */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            minHeight: "300px",
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={safeStep}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
            >
              <h3
                style={{
                  color: "var(--accent)",
                  fontSize: "1.5rem",
                  marginBottom: "1rem",
                }}
              >
                {activeItem.title}
              </h3>
              <div
                style={{
                  fontSize: "1.1rem",
                  lineHeight: "1.6",
                  color: "var(--text-main)",
                }}
              >
                {activeItem.description}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </Slide>
  );
};
