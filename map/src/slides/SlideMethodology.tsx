import React from "react";
import { Slide } from "../components/Slide";

export const SlideMethodology = () => {
  return (
    <Slide>
      <h2 className="section-title">Methodology</h2>
      <div className="image-container" style={{ height: "70vh" }}>
        <img
          src="/Full Methodology.png" // Ensure this path is correct
          alt="System Architecture"
          style={{ maxHeight: "100%" }}
        />
      </div>
    </Slide>
  );
};
