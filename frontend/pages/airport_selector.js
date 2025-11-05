// Defines a React component for selecting an airport from a list of valid options from airports.csv
// Uses fuzzy matching on both airport name and IATA code

"use client";
import { useState, useEffect } from "react";
import Fuse from "fuse.js";
import * as d3 from "d3";

export default function AirportSelector({ onSelect }) {
    const [airports, setAirports] = useState([]);
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);

    // Load airports.csv once
    useEffect(() => {
        d3.csv("/data/airports.csv").then(data => {
            // Filter to only large and medium airports
            data = data.filter(d =>
                d.type === "large_airport" || d.type === "medium_airport"
            );
            // Keep only name, ident, lat, lon
            const cleaned = data.map(d => ({
                name: d.name,
                ident: d.ident,
                lat: +d.latitude_deg,
                lon: +d.longitude_deg
            }));
            setAirports(cleaned);
        });
    }, []);

    // Create Fuse instance
    const fuse = new Fuse(airports, {
        keys: ["name", "ident"],
        threshold: 0.3 // lower = stricter
    });

    // Update search results
    useEffect(() => {
        if (query.trim().length === 0) {
            setResults([]);
        } else {
            setResults(fuse.search(query).slice(0, 8)); // top 8 matches
        }
    }, [query]);

    return (
        <div style={{ position: "relative", width: "300px" }}>
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
                        onSelect(airport);     // SAME select logic as clicking
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
                            style={{ padding: "8px", cursor: "pointer" }}
                            onClick={() => {
                                setQuery(r.item.name);
                                setResults([]);
                                onSelect(r.item); // <--- Return lat/lon upwards
                            }}
                        >
                            {r.item.name} ({r.item.ident})
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
