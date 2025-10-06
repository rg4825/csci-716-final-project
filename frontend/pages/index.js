"use client";
import { useEffect, useRef } from "react";
import * as d3 from "d3";
import * as topojson from "topojson-client";
//const versor = require("versor");

export default function Home() {
  const mapRef = useRef(null);

  useEffect(() => {
    if (mapRef.current) renderMap(mapRef.current);
  }, []);

  return (
    <main className="flex flex-col justify-center items-center min-h-screen bg-gray-100">
      <div ref={mapRef} />
    </main>
  );
}

/** Renders an interactive orthographic world map inside a container element */
function renderMap(container) {
  const width = 960;
  const height = 960;

  // Clear previous map
  d3.select(container).selectAll("*").remove();

  // Create SVG
  const svg = d3
    .select(container)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  // Define projection and path
  const projection = d3
    .geoOrthographic()
    .scale(450)
    .translate([width / 2, height / 2])
    .clipAngle(90);

  const path = d3.geoPath(projection);
  const graticule = d3.geoGraticule();

  // Draw graticule (latitude/longitude lines)
  const graticulePath = svg
    .append("path")
    .datum(graticule())
    .attr("fill", "none")
    .attr("stroke", "#999")
    .attr("stroke-width", 0.5)
    .attr("d", path);

  // Draw countries
  const gCountries = svg.append("g");

  d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then(
    (world) => {
      const countries = topojson.feature(world, world.objects.countries).features;
      gCountries
        .selectAll(".country")
        .data(countries)
        .enter()
        .append("path")
        .attr("class", "country")
        .attr("fill", "#ccc")
        .attr("stroke", "#fff")
        .attr("d", path);
    }
  );

  // Draw outline
  const outline = svg
    .append("path")
    .datum({ type: "Sphere" })
    .attr("stroke", "#000")
    .attr("fill", "none")
    .attr("stroke-width", 1)
    .attr("d", path);


  // Enable zoom & rotation 
  // (Zoom uses the pointer events, so )
  const move = d3
    .zoom()
    .scaleExtent([200, 1200])
    .on("zoom", (event) => {
      // Zoom (prevent shrinkage at start)
      if (event.transform.k > 200 && event.transform.k < 1200) {
        projection.scale(event.transform.k);
      }

      // Drag
      if (event.sourceEvent) {
        const rotate = projection.rotate();
        const k = 0.25; // Sensitivity factor
        projection.rotate([
          rotate[0] + (event.sourceEvent.movementX || 0) * k,
          rotate[1] - (event.sourceEvent.movementY || 0) * k,
        ]);
      }

      refresh();
    });

  svg.call(move);

  // Redraw map elements
  function refresh() {
    svg.selectAll(".country").attr("d", path);
    graticulePath.attr("d", path);
    outline.attr("d", path);
  }
}
