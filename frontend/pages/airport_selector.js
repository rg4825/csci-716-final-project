"use client";
import { useState, useEffect } from "react";
import Fuse from "fuse.js";
import * as d3 from "d3";

export default function AirportSelector({ onSelect }) {
    const [selectedAirport, setSelectedAirport] = useState(null);
    const [airports, setAirports] = useState([]);
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);

    // New state for simulation parameters
    const [generations, setGenerations] = useState(1);
    const [cells, setCells] = useState(5);
    const [radius, setRadius] = useState(50);

    // Load airports.csv once
    useEffect(() => {
        d3.csv("/data/airports.csv").then(data => {
            data = data.filter(d =>
                d.type === "large_airport" || d.type === "medium_airport"
            );
            const cleaned = data.map(d => ({
                name: d.name,
                ident: d.ident,
                lat: +d.latitude_deg,
                lon: +d.longitude_deg
            }));
            setAirports(cleaned);
        });
    }, []);

    // Fuse instance
    const fuse = new Fuse(airports, {
        keys: ["name", "ident"],
        threshold: 0.3
    });

    // Update search results
    useEffect(() => {
        if (query.trim().length === 0) {
            setResults([]);
        } else {
            setResults(fuse.search(query).slice(0, 8));
        }
    }, [query]);

    const handleGenerate = () => {
        if (!selectedAirport) return; // require airport selection
        onSelect({
            airport: selectedAirport,
            generations,
            cells,
            radius
        });
    };

    return (
        <div style={{ position: "relative", width: "320px", display: "flex", flexDirection: "column", gap: "12px" }}>
            {/* Airport search box */}
            <div style={{ position: "relative" }}>
                <input
                    type="text"
                    value={query}
                    placeholder="Search airport (e.g., JFK or LAX)"
                    onChange={e => setQuery(e.target.value)}
                    onKeyDown={e => {
                        if (e.key === "Enter" && results.length > 0) {
                            const airport = results[0].item;
                            setQuery(airport.name);
                            setResults([]);
                            setSelectedAirport(airport);
                        }
                    }}
                    style={{ width: "100%", padding: "8px", fontSize: "1rem" }}
                />

                {results.length > 0 && (
                    <ul style={{
                        position: "absolute",
                        top: "40px",
                        left: 0,
                        right: 0,
                        maxHeight: "200px",
                        overflowY: "auto",
                        backgroundColor: "white",
                        border: "1px solid #ccc",
                        listStyle: "none",
                        margin: 0,
                        padding: 0,
                        zIndex: 1000
                    }}>
                        {results.map(r => (
                            <li
                                key={r.item.ident}
                                style={{ padding: "8px", cursor: selectedAirport ? "pointer" : "not-allowed" }}
                                onClick={() => {
                                    setQuery(r.item.name);
                                    setResults([]);
                                    setSelectedAirport(r.item);
                                }}
                            >
                                {r.item.name} ({r.item.ident})
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {/* Simulation parameter inputs */}
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <label>
                    Generations:
                    <input
                        type="number"
                        min="0"
                        value={generations}
                        onChange={e => setGenerations(parseInt(e.target.value) || 1)}
                        style={{ width: "100%", padding: "6px" }}
                    />
                </label>

                <label>
                    Number of Cells:
                    <input
                        type="number"
                        min="0"
                        value={cells}
                        onChange={e => setCells(parseInt(e.target.value) || 1)}
                        style={{ width: "100%", padding: "6px" }}
                    />
                </label>

                <label>
                    Radius:
                    <input
                        type="number"
                        min="0"
                        value={radius}
                        onChange={e => setRadius(parseInt(e.target.value) || 1)}
                        style={{ width: "100%", padding: "6px" }}
                    />
                </label>
            </div>

            {/* Generate button */}
            <button disabled={!selectedAirport}
                onClick={handleGenerate}
                style={{
                    padding: "10px",
                    backgroundColor: "#0070f3",
                    color: "white",
                    border: "none",
                    cursor: "pointer",
                    fontSize: "1rem",
                    borderRadius: "6px"
                }}
            >
                Generate
            </button>
        </div>
    );
}
