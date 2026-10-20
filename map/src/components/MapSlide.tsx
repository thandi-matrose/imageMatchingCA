import React, { useState } from "react";
import Map, { Marker, NavigationControl } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

export const MapSlide: React.FC = () => {
  // Approximate center of Woodstock/Salt River
  const [viewState, setViewState] = useState({
    longitude: 18.438,
    latitude: -33.928,
    zoom: 13,
  });

  return (
    <div className="map-container">
      <Map
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
      >
        <NavigationControl position="top-right" />

        {/* Add a marker for the study area */}
        <Marker longitude={18.438} latitude={-33.928} anchor="bottom">
          <div
            style={{
              background: "var(--accent)",
              color: "white",
              padding: "4px 8px",
              borderRadius: "4px",
              fontSize: "12px",
              fontWeight: "bold",
            }}
          >
            Woodstock
          </div>
        </Marker>
      </Map>
    </div>
  );
};
