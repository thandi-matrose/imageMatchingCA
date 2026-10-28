import { Slide } from "../components/Slide";
import { motion } from "framer-motion";
import { highlight } from "../utils/functions";

interface SlideSignaturesProps {
  step?: number;
}

export const SlideSignatures = ({ step = 0 }: SlideSignaturesProps) => {
  const images = [
    { src: "/results/overlap/overlap_LOG_INTENSITY.png", alt: "Log Intensity" },
    {
      src: "/results/overlap/overlap_SPECKLE_DIVERGENCE.png",
      alt: "Speckle Divergence",
    },
    { src: "/results/overlap/overlap_ENERGY_GLCM.png", alt: "Energy GLCM" },
    { src: "/results/overlap/overlap_MEAN_GLCM.png", alt: "Mean GLCM" },
    { src: "/results/overlap/overlap_VARIANCE_GLCM.png", alt: "Variance GLCM" },
  ];

  return (
    <Slide>
      <h2 className="section-title">
        Radar Signatures as Degrees of Membership
      </h2>
      <div className="one-two-col">
        {/* Left Column: Text */}
        <div className=" pres-text">
          <p>
            {highlight("Trapezoidal membership functions")} are derived from the
            25th, 40th, 60th, and 75th percentiles of visually classified grid
            cells.
          </p>
        </div>

        {/* Right Column: Vertical Carousel */}
        <div className="carousel-container">
          {images.map((img, i) => {
            // Calculate position:
            // - Past images go up (-100%)
            // - Active image stays at 0%
            // - Future images wait down below (100%)
            const yPosition = `${(i - step) * 100}%`;

            return (
              <motion.div
                key={img.src}
                className="carousel-item"
                initial={false}
                animate={{
                  y: yPosition,
                  opacity: i === step ? 1 : 0.3, // Dim non-active slides slightly
                  scale: i === step ? 1 : 0.95, // Slight zoom effect on active
                }}
                transition={{
                  duration: 0.6,
                  ease: [0.32, 0.72, 0, 1], // Custom cubic-bezier for a smooth slide
                }}
              >
                <img src={img.src} alt={img.alt} />
              </motion.div>
            );
          })}
        </div>
      </div>
    </Slide>
  );
};
