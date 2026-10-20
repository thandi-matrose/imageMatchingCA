import React, { useState } from "react";
import Map, { Source, Layer } from "react-map-gl/maplibre";
import { Slide } from "../components/Slide";
import { motion, AnimatePresence } from "framer-motion";
import "maplibre-gl/dist/maplibre-gl.css";

const LAYERS = [
  {
    id: "rf",
    name: "Random Forest (Aerial)",
    color: "#4A90D9",
    url: "/rasters/rf.png", // Update with your real paths
    coordinates: [
      [18.42, -33.91],
      [18.45, -33.91],
      [18.45, -33.94],
      [18.42, -33.94],
    ],
    description:
      "Pixel-wise classification. High resolution, but lacks spatial context.",
  },
  {
    id: "growcut",
    name: "GrowCut Baseline",
    color: "#DC6868",
    url: "/rasters/growcut.png",
    coordinates: [
      [18.42, -33.91],
      [18.45, -33.91],
      [18.45, -33.94],
      [18.42, -33.94],
    ],
    description: "Binary competitive growth. Prone to sharp, noisy boundaries.",
  },
  {
    id: "sycamor",
    name: "syCAMOR",
    color: "#914545",
    url: "/rasters/sycamor.png",
    coordinates: [
      [18.42, -33.91],
      [18.45, -33.91],
      [18.45, -33.94],
      [18.42, -33.94],
    ],
    description:
      "Fuzzy CA classification. Smooth regions with transparent boundaries.",
  },
  {
    id: "match",
    name: "Registered Match",
    color: "#486a48",
    url: "/rasters/match.png",
    coordinates: [
      [18.42, -33.91],
      [18.45, -33.91],
      [18.45, -33.94],
      [18.42, -33.94],
    ],
    description:
      "Radar shifted onto the optical grid using phase cross-correlation.",
  },
];

interface SlideDemonstrationProps {
  step?: number;
  setStep?: (step: number) => void;
}

export const SlideDemonstration = ({
  step = 0,
  setStep,
}: SlideDemonstrationProps) => {
  const [viewState, setViewState] = useState({
    longitude: 18.438,
    latitude: -33.928,
    zoom: 13,
  });

  // Derive the active layer directly from the global step
  const activeLayer = LAYERS[step] || LAYERS[0];

  return (
    <Slide>
      <div className="demonstration-container">
        <Map
          {...viewState}
          onMove={(evt) => setViewState(evt.viewState)}
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
          style={{ width: "100%", height: "100%" }}
        >
          <Source
            key={activeLayer.id}
            id="raster-source"
            type="image"
            url={activeLayer.url}
            coordinates={activeLayer.coordinates}
          >
            <Layer
              id="raster-layer"
              type="raster"
              paint={{
                "raster-opacity": 0.85,
                "raster-fade-duration": 0, // Instant swap for presentations
              }}
            />
          </Source>
        </Map>

        <div className="demonstration-overlay">
          <h2 className="demo-title">Interactive Comparison</h2>

          <div className="demo-tabs">
            {LAYERS.map((layer, index) => (
              <button
                key={layer.id}
                // Clicking calls setStep, which updates the global presenter state
                onClick={() => setStep && setStep(index)}
                className={`demo-tab ${activeLayer.id === layer.id ? "active" : ""}`}
                style={{
                  borderColor:
                    activeLayer.id === layer.id ? layer.color : "transparent",
                  color:
                    activeLayer.id === layer.id
                      ? layer.color
                      : "var(--text-muted)",
                }}
              >
                {layer.name}
              </button>
            ))}
          </div>

          <div className="demo-description">
            <AnimatePresence mode="wait">
              <motion.p
                key={activeLayer.id}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                transition={{ duration: 0.2 }}
              >
                {activeLayer.description}
              </motion.p>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </Slide>
  );
};
