"use client";
import { use, useEffect, useRef } from "react";
import * as d3 from "d3";
import * as topojson from "topojson-client";
import { geoVoronoi } from "d3-geo-voronoi"; // TODO- Replace with file reading
import { geoClipPolygon } from "d3-geo-polygon";
import AirportSelector from "./airport_selector"; // Select airport from client side

import styles from "../styles/Home.module.css";

export default function Home() {
  // Refs for the three visualizations
  const globeRef = useRef(null);
  const mapRef = useRef(null);
  const twoDRef = useRef(null);
  const updateGlobeRef = useRef(null);
  const updateFlatMapRef = useRef(null);

  useEffect(() => {
    if (globeRef.current) renderMap(globeRef.current, "globe", updateGlobeRef);
    if (mapRef.current) renderMap(mapRef.current, "flat", updateFlatMapRef);
  }, []);

  return (
    <header>
      <title>Airport Voronoi Visualization</title>
    </header>,
    <main>
      <h1 className={styles.title}>Airport Voronoi Visualization</h1>
      <p className={styles.description}>
        Select an airport and explore its Voronoi cell on different map projections.
      </p>
      <AirportSelector onSelect={(airport) => {
        console.log("Selected airport:", airport);

        // Trigger GA test with selected airport 
        test_ga_async(
          airport.airport.name,
          airport.airport.lat,
          airport.airport.lon,
          airport.generations,
          airport.cells,
          airport.radius,
          updateGlobeRef,
          updateFlatMapRef
        );
      }}></AirportSelector>

      <div className={styles.container}>
        <div ref={globeRef} />
        <div ref={mapRef} />
      </div>
      <div ref={twoDRef} className={styles.twoDContainer} />
    </main>
  );
}


async function test_ga_async(airport, lat, lon, generations, cells, radius, updateGlobeRef, updateFlatMapRef) {
  console.log("Starting GA async flight vornonoi generation...");

  const url = new URL("http://localhost:8080/flight/ga_async");
  // Attach all user-selected parameters
  url.searchParams.set("airport", airport);
  url.searchParams.set("lat", lat);
  url.searchParams.set("lon", lon);
  url.searchParams.set("generations", generations);
  url.searchParams.set("cells", cells);
  url.searchParams.set("radius", radius);

  const eventSource = new EventSource(url);


  eventSource.onmessage = function (event) {
    console.log("Received GA update:", event.data);
    const data = JSON.parse(event.data);

    if (data.event === "end") {
      console.log("GA async stream finished normally.");
      eventSource.close();
      return;
    }

    console.log("GA async data from backend:", data);

    // Update 2D Voronoi visualization
    if (updateGlobeRef.current) {
      updateGlobeRef.current(data, lat, lon, radius);
    }
    if (updateFlatMapRef.current) {
      updateFlatMapRef.current(data, lat, lon, radius);
    }

  };

  console.log("GA async test setup complete.");

  eventSource.onerror = function (event) {
    if (eventSource.readyState === EventSource.CLOSED) {
      console.log("GA async stream closed normally.");
    } else {
      console.error("GA async stream error:", event);
    }
  };

}


/** --- Generalized map renderer --- **/
async function renderMap(container, type = "globe", updateFnRef) {
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

  // --- Initialize bounding box ---
  const bboxGroup = svg.append("g").attr("class", "bboxGroup");

  // --- Voronoi cells (optional) ---
  // Load airport data
  const airports = await d3.csv("/data/airports.csv", d => {
    if (d.type !== "large_airport") return null;
    return {
      name: d.name,
      lat: +d.latitude_deg,
      lon: +d.longitude_deg
    };
  });

  // Draw Voronoi cells
  const seeds = airports.map(airport => [airport.lon, airport.lat]);
  console.log("Generating Voronoi diagram with", seeds.length, "seeds");

  const voronoi = geoVoronoi(seeds);
  svg.append("g")
    .attr("class", styles.voronoiGroup)
    .selectAll("path")
    .data(voronoi.polygons().features)
    .enter()
    .append('path')
    .attr('d', path)
    .attr('class', styles.voronoiCell);

  // Draw seeds for each airport (only if type = large_airport)
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

  console.log(voronoi.polygons().features);

  // --- Setup update function ---
  updateFnRef.current = function (data, lat, lon, radius) {
    console.log("Updating Voronoi diagram with backend GA data:", data);
    // Clear existing Voronoi cells + seeds 
    clearVoronoi(svg);

    // Extract SEEDS from backend 
    const seedFeatures = data.voronoi_edges.seeds;
    const seeds = seedFeatures.map(f => {
      const [lat, lon] = f.geometry.coordinates;
      return { lat: lat, lon: lon };
    });

    // Extract POLYGONS from backend 
    const polygons = data.voronoi_edges.polygons.map(f => {
      const ring = f.geometry.coordinates.map(([lat, lon]) => [lon, lat]);
      return {
        type: "Feature", geometry: {
          type: "Polygon", coordinates: [ring] // wrap ring! 
        }
      };
    });

    // Clear old box
    svg.selectAll(".bboxGroup > *").remove();

    const bbox = getBoundingBox(lat, lon, radius);

    // Draw bounding box
    const bboxPolygon = {
      type: "Feature",
      geometry: {
        type: "Polygon",
        coordinates: [[
          [bbox.west, bbox.south],
          [bbox.east, bbox.south],
          [bbox.east, bbox.north],
          [bbox.west, bbox.north],
          [bbox.west, bbox.south]
        ]]
      }
    };

    // Draw rectangle 
    bboxGroup.append("path")
      .datum(bboxPolygon)
      .attr("class", "boundingBox")
      .attr("d", path);

    // Apply polygon to the Voronoi paths
    

    // Draw NEW seed points
    svg.append("g")
      .attr("class", "seedGroup")
      .selectAll("circle")
      .data(seeds)
      .enter()
      .append("circle")
      .attr("class", styles.airport)
      .attr("cx", d => projection([d.lon, d.lat])[0])
      .attr("cy", d => projection([d.lon, d.lat])[1]);

    // Draw NEW Voronoi cells
    svg.append("g")
      .attr("class", styles.voronoiGroup)
      .selectAll("path")
      .data(polygons)
      .enter()
      .append("path")
      .attr("class", styles.voronoiCell)
      .attr("d", path);

    console.log("Polygon sample:", polygons[0]);
    console.log("Path result:", path(polygons[0]));

    svg.selectAll("path")
      .attr("fill", "none")
      .attr("stroke", "black");
  };

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

/** --- Rotation, Zoom, and Pan --- **/
function addInteraction(svg, projection, path, width, height, type) {
  const minZoom = projection.scale();
  const maxZoom = minZoom * 100;

  // Track the current transform state
  let currentTransform = d3.zoomIdentity.scale(minZoom);

  const zoom = d3.zoom()
    .scaleExtent([minZoom, maxZoom])
    .on("zoom", event => {
      const k = event.transform.k;
      const prevK = currentTransform.k;

      // Update projection scale
      if (k >= minZoom && k < maxZoom) {
        projection.scale(k);
      }

      if (event.sourceEvent) {
        const eventType = event.sourceEvent.type;

        // Handle wheel zoom (zoom to mouse position)
        if (eventType === 'wheel') {
          if (type === "globe") {
            // Get mouse position relative to SVG
            const [mouseX, mouseY] = d3.pointer(event.sourceEvent, svg.node());

            // Invert to get geographic coordinates at mouse position
            const coords = projection.invert([mouseX, mouseY]);

            if (coords) {
              // Calculate how much to adjust rotation to keep point under mouse
              const rotate = projection.rotate();
              const scaleFactor = k / prevK;

              // Adjust rotation to zoom toward mouse position
              projection.rotate([
                rotate[0] + (coords[0] + rotate[0]) * (1 - 1 / scaleFactor) * 0.1,
                rotate[1] + (coords[1] + rotate[1]) * (1 - 1 / scaleFactor) * 0.1,
              ]);
            }

          } else if (type === "flat") {
            // For flat projection, adjust translation to zoom toward mouse
            const [mouseX, mouseY] = d3.pointer(event.sourceEvent, svg.node());
            const translate = projection.translate();

            // Calculate the offset from center
            const dx = mouseX - translate[0];
            const dy = mouseY - translate[1];

            // Adjust translation proportional to zoom change
            const scaleFactor = k / prevK;
            const newTranslateX = mouseX - dx * scaleFactor;
            const newTranslateY = mouseY - dy * scaleFactor;

            // Apply bounds
            const newX = Math.min(50 + (3 * k), Math.max(width - 50 - (3 * k), newTranslateX));
            const newY = Math.min(50 + (3 * k), Math.max(height - 50 - (3 * k), newTranslateY));

            projection.translate([newX, newY]);
          }
        }
        // Handle drag (rotation/pan)
        else if (eventType === 'mousemove' || eventType === 'pointermove') {
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
      }

      // Update current transform
      currentTransform = event.transform;

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
  svg.selectAll(".boundingBox").attr("d", path);
}

/**--- Clear Points and Cells --- */
function clearVoronoi(svg) {
  svg.selectAll(`.${styles.voronoiCell}`).remove();
  svg.selectAll("circle").remove();
}


/** --- Geodesic utility functions --- */
function geodesicDestination(lat, lon, distanceMiles, bearingDeg) {
  const R = 3958.8; // Earth radius in miles
  const brng = bearingDeg * Math.PI / 180;
  const dR = distanceMiles / R;

  const lat1 = lat * Math.PI / 180;
  const lon1 = lon * Math.PI / 180;

  const lat2 = Math.asin(
    Math.sin(lat1) * Math.cos(dR) +
    Math.cos(lat1) * Math.sin(dR) * Math.cos(brng)
  );

  const lon2 = lon1 + Math.atan2(
    Math.sin(brng) * Math.sin(dR) * Math.cos(lat1),
    Math.cos(dR) - Math.sin(lat1) * Math.sin(lat2)
  );

  return {
    lat: lat2 * 180 / Math.PI,
    lon: lon2 * 180 / Math.PI
  };
}

function getBoundingBox(lat, lon, miles) {
  const sw = geodesicDestination(lat, lon, miles, 225);
  const ne = geodesicDestination(lat, lon, miles, 45);

  return {
    west: sw.lon,
    south: sw.lat,
    east: ne.lon,
    north: ne.lat
  };
}