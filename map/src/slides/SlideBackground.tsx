import { Slide } from "../components/Slide";
import { motion } from "framer-motion";

interface SlideBackgroundProps {
  step?: number;
}

const POINTS = [
  {
    label: "Why radar?",
    text: "Woodstock and Salt River are redeveloping fast. Optical imagery is blocked by cloud and darkness, while SAR images the surface in any weather, day or night, so it can track change on a regular schedule.",
  },
  {
    label: "Why matching it is hard?",
    text: "Speckle noise, layover, foreshortening and shadow have no counterpart in optical images. In a benchmark of sixteen registration algorithms on over 10,000 image pairs, none succeeded every time, and most failed on sub-metre data.",
    source: "W. Zhang et al., 2025",
  },
  {
    label: "The crucial gap",
    text: "Deep learning can match these images but cannot explain its decisions, which matters when planners and residents rely on the result. Cellular automata are fully inspectable, yet rarely applied to SAR-optical matching. syCAMOR fills that gap.",
  },
];

export const SlideBackground = ({ step = 0 }: SlideBackgroundProps) => {
  return (
    <Slide>
      <h2 className="section-title">Background</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
        {POINTS.map((pt, i) => (
          <motion.div
            key={pt.label}
            className="one-two-col pres-text"
            initial={false}
            animate={{
              opacity: i > step ? 0 : i === step ? 1 : 0.45,
              y: i > step ? 20 : 0,
            }}
            transition={{ duration: 0.4 }}
            style={{
              borderLeft: "4px solid var(--accent)",
              paddingLeft: "1.5rem",
              alignItems: "start",
            }}
          >
            <h3
              className="background-label"
              style={{ fontSize: "1.5rem", margin: 0 }}
            >
              {pt.label}
            </h3>
            <div>
              <p style={{ margin: 0 }}>{pt.text}</p>
              {pt.source && (
                <p
                  style={{
                    margin: "0.5rem 0 0",
                    fontSize: "0.9rem",
                    color: "var(--text-muted)",
                  }}
                >
                  {pt.source}
                </p>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </Slide>
  );
};
