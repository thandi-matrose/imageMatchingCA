import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer } from "react-leaflet";

import "maplibre-gl/dist/maplibre-gl.css";

const ParallaxMapSection = () => {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      // Find the scroll container (presentation-container)
      const container = document.querySelector("#root");
      if (container) {
        setScrollY(container.scrollTop);
      }
    };

    const container = document.querySelector("#root");
    if (container) {
      container.addEventListener("scroll", handleScroll);
    }
    return () => {
      if (container) {
        container.removeEventListener("scroll", handleScroll);
      }
    };
  }, []);
  // Optional: Append ?api_key=YOUR_API_KEY if authenticated
  const tileUrl =
    "https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}{r}.png?api_key=5cd65dcb-f8d5-4b7d-91ef-ae28b3e85c14";

  const attribution = `
    &copy; <a href="https://stadiamaps.com/attribution/" target="_blank">Stadia Maps</a> 
    &copy; <a href="https://stamen.com/" target="_blank">Stamen Design</a> 
    &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> 
    &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>
  `;
  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        zIndex: 0,
        pointerEvents: "none", // Let clicks pass through to the presentation
        // Subtle parallax transform based on scroll
        transform: `translateY(${scrollY * 0.15}px) scale(1.1)`,
        transition: "transform 0.1s ease-out",
      }}
    >
      <MapContainer
        center={[18.438, -33.928]} // New York City
        zoom={12}
        style={{ height: "100vh", width: "100%" }}
      >
        <TileLayer url={tileUrl} attribution={attribution} maxZoom={20} />
      </MapContainer>
    </div>
  );
};

export default ParallaxMapSection;
