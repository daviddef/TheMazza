/* How far apart the three home towns are, worked out from the coordinates the Atlas page already
   plots (the gazetteer in tools/atlas.py), so no prose has to carry a typed distance. */
import atlas from "../../public/atlas-data.json";

const TOWNS = ["Piedimonte Etneo", "Briatico", "Scilla"];

function km(a, b) {
  const R = 6371, rad = (d) => (d * Math.PI) / 180;
  const dLat = rad(b.lat - a.lat), dLon = rad(b.lon - a.lon);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

const pts = TOWNS.map((t) => atlas.places.find((p) => p.name === t)).filter((p) => p && p.lat != null);
let far = 0;
for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) far = Math.max(far, km(pts[i], pts[j]));

/* Straight-line distance between the furthest two of the three towns, to the nearest ten kilometres. */
export const FURTHEST_KM = pts.length === TOWNS.length ? Math.round(far / 10) * 10 : null;
