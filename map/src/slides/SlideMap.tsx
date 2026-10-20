import React from "react";
import { Slide } from "../components/Slide";
import { MapSlide } from "../components/MapSlide";
import { InlineMath } from "react-katex";

export const SlideMap = () => {
  return (
    <Slide>
      <h2 className="section-title">Study Area: Woodstock & Salt River</h2>
      <div className="two-col">
        <div>
          <p>
            An area of ~4.2 km² experiencing rapid gentrification. We need
            transparent, temporal tools to monitor urban change against
            all-weather SAR and 5cm aerial imagery.
          </p>
          <p>
            Coordinates are mapped in <InlineMath math="Lo19" /> (Gauss
            Conformal).
          </p>
        </div>
        <MapSlide />
      </div>
    </Slide>
  );
};
