import React from "react";
import { Slide } from "../components/Slide";
import { motion } from "framer-motion";

interface SlideImpactProps {
  step?: number;
}

const VOICES = [
  {
    icons: ["icons/urban-planning.png", "icons/activism.png"],
    who: "The planner",
    text: "Assessing a development against the local spatial framework, they must be able to interrogate the basis of a model's output.",
  },
  {
    icons: ["icons/urban-planning.png", "icons/activism.png"],
    who: "The activist",
    text: "Contesting an eviction order, they must be able to scrutinise the evidence presented against their community.",
  },
];
/*
const map = (
  <div className="two-col" style={{ alignItems: "stretch" }}>
    {VOICES.map((v) => (
      <motion.div
        key={v.who}
        initial={false}
        animate={{ opacity: step >= 1 ? 1 : 0, y: step >= 1 ? 0 : 20 }}
        transition={{ duration: 0.5 }}
        className="who-box"
      >
        <div className="who-icons">
          <img src={v.icons[0]} />
          <img src={v.icons[1]} />
        </div>
        <h3 style={{ fontSize: "1.5rem", marginTop: 0 }}>{v.who}</h3>
        <p style={{ margin: 0 }}>{v.text}</p>
      </motion.div>
    ))}
  </div>
);*/
export const SlideImpact = ({ step = 0 }: SlideImpactProps) => {
  return (
    <Slide>
      <div className="two-col" style={{ maxWidth: "900px" }}>
        <img style={{ width: "300px" }} src="icons/black-box.png" />
        <h2 className="section-title">Who gets to check the model?</h2>
      </div>
      <motion.p
        initial={false}
        animate={{ opacity: step >= 2 ? 1 : 0 }}
        transition={{ duration: 0.5 }}
        style={{ marginTop: "2.5rem", fontSize: "1.5rem", textAlign: "center" }}
      >
        With <span className="robo">syCAMOR</span>, every cell state, rule and
        decision can be traced.
      </motion.p>
    </Slide>
  );
};
