// pages/index.js
"use client";
import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import * as topojson from "topojson-client";

// --- Versor utilities (adapted from Jason Davies)
function versor([λ, φ, γ]) {
  λ *= Math.PI / 180;
  φ *= Math.PI / 180;
  γ *= Math.PI / 180;
  const sl = Math.sin(λ), cl = Math.cos(λ);
  const sp = Math.sin(φ), cp = Math.cos(φ);
  const sg = Math.sin(γ), cg = Math.cos(γ);
  return [
    cl * cp * cg + sl * sp * sg,
    sl * cp * cg - cl * sp * sg,
    cl * sp * cg + sl * cp * sg,
    cl * cp * sg - sl * sp * cg,
  ];
}

function versorMultiply([a, b, c, d], [e, f, g, h]) {
  return [
    a * e - b * f - c * g - d * h,
    a * f + b * e + c * h - d * g,
    a * g - b * h + c * e + d * f,
    a * h + b * g - c * f + d * e,
  ];
}

function versorToEuler([a, b, c, d]) {
  return [
    Math.atan2(2 * (a * b + c * d), 1 - 2 * (b * b + c * c)) * 180 / Math.PI,
    Math.asin(Math.max(-1, Math.min(1, 2 * (a * c - d * b)))) * 180 / Math.PI,
    Math.atan2(2 * (a * d + b * c), 1 - 2 * (c * c + d * d)) * 180 / Math.PI,
  ];
}

function eulerToVersor(euler) {
  return versor(euler);
}

export default function Home() {
  const mapRef = useRef();
  const [autoSpin, setAutoSpin] = useState(false);

  useEffect(() => {
    const width = 960;
    const height = 960;

    d3.select(mapRef.current).selectAll("*").remove();

    const svg = d3
      .select(mapRef.current)
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    const projection = d3
      .geoOrthographic()
      .scale(450)
      .translate([width / 2, height / 2])
      .clipAngle(90);

    const path = d3.geoPath().projection(projection);

    const graticule = d3.geoGraticule();

    const graticulePath = svg
      .append("path")
      .datum(graticule())
      .attr("class", "graticule")
      .attr("d", path)
      .attr("fill", "none")
      .attr("stroke", "#999")
      .attr("stroke-width", 0.5);

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
          .attr("d", path)
          .attr("fill", "#ccc")
          .attr("stroke", "#fff");
      }
    );

    // --- Rotation using versors ---
    let currentEuler = [0, 0, 0];
    let q0, r0, p0;

    const drag = d3.drag()
      .on("start", (event) => {
        q0 = eulerToVersor(currentEuler);
        r0 = projection.rotate();
        p0 = [event.x, event.y];
      })
      .on("drag", (event) => {
        if (!p0) return;
        const p1 = [event.x, event.y];
        const dx = p1[0] - p0[0];
        const dy = p1[1] - p0[1];
        const q1 = eulerToVersor([dx * 0.5, -dy * 0.5, 0]);
        const q = versorMultiply(q1, q0);
        currentEuler = versorToEuler(q);
        projection.rotate(currentEuler);
        refresh();
      })
      .on("end", () => {
        p0 = null;
      });

    svg.call(drag);

    // --- Auto-spin ---
    let timer;
    function startSpin() {
      if (timer) timer.stop();
      timer = d3.timer(() => {
        currentEuler[0] += 0.2; // spin speed (deg per tick)
        projection.rotate(currentEuler);
        refresh();
      });
    }

    function stopSpin() {
      if (timer) timer.stop();
      timer = null;
    }

    if (autoSpin) startSpin();
    else stopSpin();

    // --- Interaction: Zoom ---
    const zoom = d3
      .zoom()
      .scaleExtent([200, 1200]) // min/max zoom
      .on("zoom", (event) => {
        projection.scale(event.transform.k);
        refresh();
      });

    svg.call(zoom);

    function refresh() {
      svg.selectAll(".country").attr("d", path);
      graticulePath.attr("d", path);
    }

    return () => {
      if (timer) timer.stop();
    };
  }, [autoSpin]);

  return (
    <main className="flex flex-col justify-center items-center min-h-screen bg-gray-100">
      <div ref={mapRef} />
      <button
        onClick={() => setAutoSpin((s) => !s)}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
      >
        {autoSpin ? "Stop Auto-Spin" : "Start Auto-Spin"}
      </button>
    </main>
  );
}
