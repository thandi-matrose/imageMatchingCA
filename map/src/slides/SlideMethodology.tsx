import React, { useEffect, useRef, useState } from "react";
import { animate, AnimatePresence, motion } from "framer-motion";
import { Slide } from "../components/Slide";

/*
  Copy into public/figures/:
  JointMethodology.svg, seed.png, frame.gif,
  W08A_1_radar.png and the five W08A_1_Feature_*.png files.

  Each step moves a "camera" (the viewBox) to a focus box on the joint
  diagram and masks everything outside it, so it appears to pan and zoom.
  If a framing is off, nudge the numbers in box(x, y, w, h) below. They are
  measured on a 1600px-wide preview of the diagram.
*/

interface Box {
  x: number;
  y: number;
  w: number;
  h: number;
}
interface Props {
  step?: number;
  setStep?: (step: number) => void;
}

const SVG_W = 6749.34;
const SVG_H = 1746.06;
const K = SVG_W / 1600;
const box = (x: number, y: number, w: number, h: number): Box => ({
  x: x * K,
  y: y * K,
  w: w * K,
  h: h * K,
});
const BIG = 20000;
const F = "/figures/";

const STEPS: {
  label: string;
  title: string;
  caption: string;
  focus: Box;
  column: boolean;
}[] = [
  {
    label: "Retrieve",
    title: "API retrieval → radar images",
    caption:
      "Sentinel-1 GRD scenes are pulled from the Copernicus Data Hub API and cut into a radar sample set.",
    focus: box(480, 0, 340, 120),
    column: true,
  },
  {
    label: "Sample",
    title: "Sample set → trapezoidal membership functions",
    caption:
      "Visually classified cells in the sample set give every class a trapezoid [a, b, c, d] for each radar feature.",
    focus: box(665, 55, 165, 140),
    column: false,
  },
  {
    label: "Extract",
    title: "Feature extraction",
    caption:
      "One radar image becomes five bands: log intensity, speckle divergence, and GLCM energy, mean and variance.",
    focus: box(0, 240, 475, 182),
    column: false,
  },
  {
    label: "Seed",
    title: "Seeding",
    caption:
      "Only cells whose membership clears the seeding threshold (0.80) get a class. Every other cell stays undefined.",
    focus: box(650, 215, 300, 170),
    column: false,
  },
  {
    label: "Grow",
    title: "Region growing",
    caption:
      "The transition rule spreads classes from the seeds through each cell's neighbourhood until no undefined cells remain.",
    focus: box(1085, 190, 515, 210),
    column: false,
  },
];

const THUMBS = [
  { src: "W08A_1_radar.png", label: "Original Radar image" },
  {
    src: "W08A_1_Feature_LOG_INTENSITY.png",
    label: " Band 1: Log intensity",
  },
  {
    src: "W08A_1_Feature_SPECKLE_DIVERGENCE.png",
    label: "Band 2: Speckle divergence",
  },
  { src: "W08A_1_Feature_ENERGY_GLCM.png", label: "Band 3: GLCM energy" },
  { src: "W08A_1_Feature_MEAN_GLCM.png", label: "Band 4: GLCM mean" },
  { src: "W08A_1_Feature_VARIANCE_GLCM.png", label: "Band 5: GLCM variance" },
];

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// Smoothly moves the camera between focus boxes.
function useCamera(target: Box): Box {
  const [box, setBox] = useState(target);
  const current = useRef(target);
  useEffect(() => {
    const from = { ...current.current };
    const ctrl = animate(0, 1, {
      duration: 0.9,
      ease: [0.32, 0.72, 0, 1],
      onUpdate: (t) => {
        const b = {
          x: lerp(from.x, target.x, t),
          y: lerp(from.y, target.y, t),
          w: lerp(from.w, target.w, t),
          h: lerp(from.h, target.h, t),
        };
        current.current = b;
        setBox(b);
      },
    });
    return () => ctrl.stop();
  }, [target]);
  return box;
}

const TrapezoidPlot = () => (
  <svg viewBox="0 0 300 220" style={{ width: "100%" }}>
    <line x1="30" y1="180" x2="280" y2="180" stroke="#999" />
    <line x1="30" y1="20" x2="30" y2="180" stroke="#999" />
    <motion.path
      d="M50 180 L100 50 L180 50 L250 180"
      fill="none"
      stroke="#9f5272"
      strokeWidth="4"
      strokeLinejoin="round"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 1.2 }}
    />
    <motion.path
      d="M50 180 L100 50 L180 50 L250 180 Z"
      fill="#946388"
      initial={{ opacity: 0 }}
      animate={{ opacity: 0.12 }}
      transition={{ delay: 1.1, duration: 0.6 }}
    />
    {[
      ["a", 50, 180],
      ["b", 100, 50],
      ["c", 180, 50],
      ["d", 250, 180],
    ].map(([t, x, y], i) => (
      <motion.text
        key={t as string}
        x={x as number}
        y={(y as number) + (i === 0 || i === 3 ? 22 : -10)}
        textAnchor="middle"
        fontSize="16"
        fontStyle="italic"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 + i * 0.25 }}
      >
        {t as string}
      </motion.text>
    ))}
    <text x="24" y="54" textAnchor="end" fontSize="12">
      1
    </text>
    <text x="155" y="206" textAnchor="middle" fontSize="12" fill="#666">
      feature value
    </text>
  </svg>
);

const Panel = ({ step, column }: { step: number; column: boolean }) => {
  const card: React.CSSProperties = {
    width: "100%",
    border: "1px solid #ddd",
    borderRadius: 6,
    display: "block",
  };
  // In column mode the panel is a short strip, so single images shrink to fit its height.
  const single: React.CSSProperties = column
    ? {
        ...card,
        width: "auto",
        maxWidth: "100%",
        margin: "0 auto",
      }
    : card;
  const wrap: React.CSSProperties = column ? { height: "100%" } : {};
  const cap: React.CSSProperties = {
    fontSize: "0.8rem",
    color: "var(--text-muted)",
    margin: "0.3rem 0 0",
    textAlign: "center",
  };
  if (step === 0)
    return (
      <div style={wrap}>
        <img src={F + "W08A_1_radar.png"} alt="Radar tile" style={single} />
        <p style={cap}>Sentinel-1 Tile W08A_1</p>
      </div>
    );
  if (step === 1) return <TrapezoidPlot />;
  if (step === 2)
    return (
      <div
        id="thumbnails"
        style={{
          gap: "0.75rem",
        }}
      >
        {THUMBS.map((t, i) => (
          <motion.div
            key={t.src}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.12 }}
          >
            <img src={F + t.src} alt={t.label} style={card} />
            <p style={cap}>{t.label}</p>
          </motion.div>
        ))}
      </div>
    );
  if (step === 3)
    return (
      <div style={wrap}>
        <img src={F + "seed.gif"} alt="Seed maps" style={single} />
        <p style={cap}>Seeds across the study-area tiles</p>
      </div>
    );
  return (
    <div style={wrap}>
      <img src={F + "frame.gif"} alt="Region growing" style={single} />
      <p style={cap}>One frame per generation</p>
    </div>
  );
};

export const SlideMethodology = ({ step = 0, setStep }: Props) => {
  const s = Math.min(step, STEPS.length - 1);
  const f = useCamera(STEPS[s].focus);
  const pad = 0.05 * Math.max(f.w, f.h);
  const column = STEPS[s].column; // wide framings stack the panel below the diagram

  return (
    <Slide>
      <h2 className="section-title">Methodology</h2>

      <div id="meth-nav" style={{ gap: "0.5rem", marginBottom: "0.75rem" }}>
        {STEPS.map((st, i) => (
          <button
            key={st.label}
            onClick={() => setStep?.(i)}
            style={{
              flex: 1,
              padding: "0.5rem",
              cursor: "pointer",
              fontFamily: "inherit",
              fontSize: "0.95rem",
              background: i === s ? "var(--accent-light)" : "transparent",
              border: "none",
              borderBottom: `3px solid ${i <= s ? "var(--accent)" : "#ddd"}`,
              color: i === s ? "var(--accent)" : "var(--text-muted)",
              fontWeight: i === s ? 700 : 400,
              transition: "all 0.3s",
            }}
          >
            {i + 1}. {st.label}
          </button>
        ))}
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: column ? "column" : "row",
          gap: "1rem",
          height: "54vh",
          background: "white",
          borderRadius: 12,
          padding: "1rem",
        }}
      >
        <svg
          viewBox={`${f.x - pad} ${f.y - pad} ${f.w + 2 * pad} ${f.h + 2 * pad}`}
          style={{ flex: 1, minWidth: 0, minHeight: 0 }}
        >
          <image
            href={F + "JointMethodology.svg"}
            x={0}
            y={0}
            width={SVG_W}
            height={SVG_H}
          />

          {/* white masks hide everything outside the focus box */}
          <rect
            x={-BIG}
            y={f.y - BIG}
            width={2 * BIG}
            height={BIG}
            fill="white"
          />
          <rect
            x={-BIG}
            y={f.y + f.h}
            width={2 * BIG}
            height={BIG}
            fill="white"
          />
          <rect x={f.x - BIG} y={f.y} width={BIG} height={f.h} fill="white" />
          <rect x={f.x + f.w} y={f.y} width={BIG} height={f.h} fill="white" />
        </svg>

        <div
          style={{
            flex: column ? "0 0 32%" : "0 0 30%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div style={{ width: "100%", height: column ? "100%" : "auto" }}>
            <AnimatePresence mode="wait">
              <motion.div
                key={s}
                initial={{ opacity: 0, x: column ? 0 : 30 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.35 }}
                style={column ? { height: "100%" } : undefined}
              >
                <Panel step={s} column={column} />
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={s}
          className="pres-text"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          style={{ marginTop: "0.75rem" }}
        >
          <p style={{ margin: 0, fontSize: "1.1rem" }}>
            <strong>{STEPS[s].title}.</strong> {STEPS[s].caption}
          </p>
        </motion.div>
      </AnimatePresence>
    </Slide>
  );
};
