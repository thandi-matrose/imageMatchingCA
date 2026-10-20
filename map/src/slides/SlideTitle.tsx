import React from "react";
import { Slide } from "../components/Slide";

export const SlideTitle = () => {
  const currentDate = new Intl.DateTimeFormat("en-UK", {
    dateStyle: "full",
  }).format(new Date());

  return (
    <Slide id="title">
      <div className="title-slide">
        <p>Honours Thesis</p>
        <h1>syCAMOR</h1>
        <h2>Cellular Automata-based Matching of Optical and Radar Imagery</h2>
        <div className="more-info">
          <p>
            Thandi Matrose
            <br />
            MTRTHA003
          </p>

          <p>Supervised by Dr Moreblessings Shoko</p>
        </div>

        <p>{currentDate}</p>
      </div>
    </Slide>
  );
};
