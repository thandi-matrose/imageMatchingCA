import { useState } from "react";
import { Slide } from "../components/Slide";
import { MapSlide } from "../components/MapSlide";
import { InlineMath } from "react-katex";

// Copy Zoning.jpg into public/figures/
export const SlideMap = () => {
  const [view, setView] = useState<"map" | "zoning">("map");

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
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
            <button
              className={`demo-tab ${view === "map" ? "active" : ""}`}
              onClick={() => setView("map")}
            >
              Live map
            </button>
            <button
              className={`demo-tab ${view === "zoning" ? "active" : ""}`}
              onClick={() => setView("zoning")}
            >
              Zoning
            </button>
          </div>
        </div>
        {view === "map" ? (
          <MapSlide />
        ) : (
          <div className="image-container">
            <img
              src="Zoning.jpg"
              alt="Zoning categories in Woodstock and Salt River"
            />
          </div>
        )}
      </div>
    </Slide>
  );
};
