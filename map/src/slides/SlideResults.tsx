import React from "react";
import { Slide } from "../components/Slide";

export const SlideResults = () => {
  return (
    <Slide>
      <h2 className="section-title">Classification Results</h2>
      <div className="two-col">
        <div className="image-container">
          <img src="/path-to-your-figure/seeding-maps.png" alt="Seeding Maps" />
        </div>
        <div>
          <p>
            <strong>Seeding:</strong> Applied an 80th-percentile threshold,
            seeding only ~3% of the 1.06 million cells.
          </p>
          <p>
            <strong>Growth:</strong> The CA expands these seeds iteratively
            using the IDW neighbourhood rule until full coverage is reached.
          </p>
        </div>
      </div>
    </Slide>
  );
};
