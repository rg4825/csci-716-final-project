"use client";
import { useEffect, useRef } from "react";
import * as d3 from "d3";
import * as topojson from "topojson-client";
import { geoVoronoi } from "d3-geo-voronoi"; // TODO- Replace with file reading

import styles from "../styles/Home.module.css";

export default function Home() {
  const globeRef = useRef(null);
  const mapRef = useRef(null);

  useEffect(() => {
    if (globeRef.current) renderGlobe(globeRef.current);
    if (mapRef.current) renderFlatMap(mapRef.current);
  }, []);

  return (
    <main className={styles.container}>
      <div ref={globeRef} />
      <div ref={mapRef} />
    </main>
  );
}

/** --- 3D Orthographic Globe --- **/
function renderGlobe(container) {
  // Clear previous contents
  d3.select(container).selectAll("*").remove();
  const width = container.clientWidth;
  const height = container.clientHeight;

  const svg = d3.select(container).append("svg");
  const projection = d3.geoOrthographic() // Centered
    .translate([width / 2, height / 2])
    .scale((Math.min(width, height) / 2.1))
    .clipAngle(90);
  const path = d3.geoPath(projection);
  const graticule = d3.geoGraticule();

  svg.append("path")
    .datum(graticule())
    .attr("class", styles.graticule)
    .attr("d", path);

  const gCountries = svg.append("g").attr("class", styles.countriesGroup);

  d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then(world => {
    const countries = topojson.feature(world, world.objects.countries).features;
    gCountries.selectAll("path")
      .data(countries)
      .enter()
      .append("path")
      .attr("class", styles.country)
      .attr("d", path);
  });

  svg.append("path")
    .datum({ type: "Sphere" })
    .attr("class", styles.outline)
    .attr("d", path);

  mapInteraction(svg, projection, path);
  refresh(svg, path);
}

/** --- 2D Mercator Map --- **/
function renderFlatMap(container) {
  // Clear previous contents
  d3.select(container).selectAll("*").remove();
  const width = container.clientWidth;
  const height = container.clientHeight;

  const svg = d3.select(container).append("svg");

  const projection = d3.geoMercator() // Centered
    .translate([width / 2, height / 2])
    .scale(width / (2 * Math.PI));
  const path = d3.geoPath(projection);
  const graticule = d3.geoGraticule();

  svg.append("path")
    .datum(graticule())
    .attr("class", styles.graticule)
    .attr("d", path);

  const gCountries = svg.append("g").attr("class", styles.countriesGroup);
  d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then(world => {
    const countries = topojson.feature(world, world.objects.countries).features;
    gCountries.selectAll("path")
      .data(countries)
      .enter()
      .append("path")
      .attr("class", styles.country)
      .attr("d", path);
  });

  // --- Zoom + Pan Bounds ---
  const minZoom = projection.scale();
  const maxZoom = minZoom * 8;

  const zoom = d3.zoom()
    .scaleExtent([minZoom, maxZoom])
    .translateExtent([
      [0, 0],
      [width, height]
    ])
    .on("zoom", event => {
      const k = event.transform.k;
      const translate = projection.translate();

      if (event.transform.k >= minZoom && event.transform.k < maxZoom) {
        projection.scale(event.transform.k);
      }
      if (event.sourceEvent) {
        const translate = projection.translate();
        const translateX = Math.min(50 + (3 * k), Math.max(width - 50 - (3 * k), translate[0] + (event.sourceEvent.movementX || 0)));
        const translateY = Math.min(50 + (3 * k), Math.max(height - 50 - (3 * k), translate[1] + (event.sourceEvent.movementY || 0)));
        projection.translate([
          translateX,
          translateY,
        ]);

        console.log("Scale:", k);
        console.log("Dimensions:", width, height);
        console.log("Translate:", projection.translate());

      }
      refresh(svg, path);
    });

  svg.call(zoom);
  svg.call(zoom.transform, d3.zoomIdentity.scale(projection.scale())); // Initialize zoom

}

/** --- Interaction --- **/
function mapInteraction(svg, projection, path) {
  const minZoom = projection.scale();
  const maxZoom = minZoom * 8;

  const zoom = d3.zoom()
    .scaleExtent([minZoom, maxZoom])
    .on("zoom", event => {
      if (event.transform.k >= minZoom && event.transform.k < maxZoom) {
        projection.scale(event.transform.k);
      }
      if (event.sourceEvent) {
        const rotate = projection.rotate();
        const k = 0.25;
        projection.rotate([
          rotate[0] + (event.sourceEvent.movementX || 0) * k,
          rotate[1] - (event.sourceEvent.movementY || 0) * k,
        ]);
      }
      refresh(svg, path);
    });

  svg.call(zoom);
}

/** --- Redraw elements --- **/
function refresh(svg, path) {
  svg.selectAll(`.${styles.country}`).attr("d", path);
  svg.selectAll(`.${styles.graticule}`).attr("d", path);
  svg.selectAll(`.${styles.outline}`).attr("d", path);
}
