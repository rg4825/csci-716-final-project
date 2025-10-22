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
    if (globeRef.current) renderMap(globeRef.current, "globe");
    if (mapRef.current) renderMap(mapRef.current, "flat");
  }, []);

  return (
    <main className={styles.container}>
      <div ref={globeRef} />
      <div ref={mapRef} />
    </main>
  );
}

/** --- Generalized map renderer --- **/
async function renderMap(container, type = "globe") {
  // --- Setup ---
  const width = container.clientWidth;
  const height = container.clientHeight;
  d3.select(container).selectAll("*").remove();

  const svg = d3.select(container).append("svg");
  const projection = createProjection(type, width, height);
  const path = d3.geoPath(projection);
  const graticule = d3.geoGraticule();

  // --- Draw base map ---
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

  // --- Sphere outline (only for globe) ---
  if (type === "globe") {
    svg.append("path")
      .datum({ type: "Sphere" })
      .attr("class", styles.outline)
      .attr("d", path);
  }

  // --- Voronoi cells (optional) ---
  // Draw seeds for each airport (only if type = large_airport)
  const airports = await d3.csv("/data/airports.csv", d => {
    if (d.type !== "large_airport") return null;
    return {
      name: d.name,
      lat: +d.latitude_deg,
      lon: +d.longitude_deg
    };
  });

  svg
    .append("g")
    .selectAll("circle")
    .data(airports)
    .enter()
    .append("circle")
    .attr("class", styles.airport)
    .attr("cx", d => projection([d.lon, d.lat])[0])
    .attr("cy", d => projection([d.lon, d.lat])[1])
    .append("title")
    .text(d => d.name);

  // Filter out airports on the far side
  if (type === "globe") {
    filter_far_side(svg, projection);
  }

  // Draw Voronoi cells
  const seeds = airports.map(airport => [airport.lon, airport.lat]);
  console.log("Generating Voronoi diagram with", seeds.length, "seeds");
  //const voronoi = geoVoronoi(seeds);
  const points = [[10, 10], [20, 20], [30, 10], [20, 5], [25, 15]];
  const voronoi = geoVoronoi(points);
  console.log(voronoi.polygons().features);
  svg.append("g")
    .attr("class", styles.voronoiGroup)
    .selectAll("path")
    .data(voronoi.polygons().features)
    .enter()
    .append('path')
    .attr('d', path)
    .attr('class', styles.voronoiCell);

  // --- Interaction ---
  addInteraction(svg, projection, path, width, height, type);

  // --- Initial draw ---
  refresh(svg, path);
}

function filter_far_side(svg, projection) {
  svg.selectAll("circle")
    .attr("display", d => {
      const gdistance = d3.geoDistance([-projection.rotate()[0], -projection.rotate()[1]], [d.lon, d.lat]);
      return gdistance < Math.PI / 2 ? null : "none";
    });
}


/** --- Projection factory --- **/
function createProjection(type, width, height) {
  if (type === "globe") {
    return d3.geoOrthographic()
      .translate([width / 2, height / 2])
      .scale(Math.min(width, height) / 2.1)
      .clipAngle(90);
  } else {
    return d3.geoMercator()
      .translate([width / 2, height / 2])
      .scale(width / (2 * Math.PI));
  }
}

/** --- Globe Rotation --- **/
function addInteraction(svg, projection, path, width, height, type) {
  const minZoom = projection.scale();
  const maxZoom = minZoom * 8;

  const zoom = d3.zoom()
    .scaleExtent([minZoom, maxZoom])
    .on("zoom", event => {
      const k = event.transform.k;

      if (k >= minZoom && k < maxZoom) {
        projection.scale(k);
      }

      if (event.sourceEvent) {
        if (type === "globe") {
          const rotate = projection.rotate();
          const sensitivity = 1 / (k / 100); // Sensitivity decreases as zoom increases
          projection.rotate([
            rotate[0] + (event.sourceEvent.movementX || 0) * sensitivity,
            rotate[1] - (event.sourceEvent.movementY || 0) * sensitivity,
          ]);
          // Filter out airports on the far side
          filter_far_side(svg, projection);

        } else if (type === "flat") {
          const translate = projection.translate();
          const translateX = translate[0] + (event.sourceEvent.movementX || 0);
          const translateY = translate[1] + (event.sourceEvent.movementY || 0);
          const newX = Math.min(50 + (3 * k), Math.max(width - 50 - (3 * k), translateX));
          const newY = Math.min(50 + (3 * k), Math.max(height - 50 - (3 * k), translateY));
          projection.translate([newX, newY]);
        }
      }
      refresh(svg, path);
    });

  svg.call(zoom);
  svg.call(zoom.transform, d3.zoomIdentity.scale(projection.scale())); // Sync initial scale
}


/** --- Redraw elements --- **/
function refresh(svg, path) {
  svg.selectAll(`.${styles.country}`).attr("d", path);
  svg.selectAll(`.${styles.graticule}`).attr("d", path);
  svg.selectAll(`.${styles.outline}`).attr("d", path);
  svg.selectAll("circle")
    .attr("cx", d => path.projection()([d.lon, d.lat])[0])
    .attr("cy", d => path.projection()([d.lon, d.lat])[1]);
  svg.selectAll(`.${styles.voronoiCell}`).attr("d", path);
}
