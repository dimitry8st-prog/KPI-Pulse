import React from "react";
import {interpolate, useCurrentFrame} from "remotion";
import {dipMonths, tableHeader, tableRows} from "../data";
import {colors} from "../theme";
import {fontFamily} from "./ui";

export const Spreadsheet: React.FC<{
  width: number;
  height: number;
  glow?: boolean;
}> = ({width, height, glow = false}) => {
  const frame = useCurrentFrame();
  const pulse = 0.45 + 0.55 * (0.5 + 0.5 * Math.sin(frame / 6));
  return (
    <div
      style={{
        width,
        height,
        background: "#0E1626",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: 16,
        overflow: "hidden",
        fontFamily,
        boxShadow: glow ? "0 20px 60px rgba(255,75,75,0.18)" : "0 20px 50px rgba(0,0,0,0.28)",
      }}
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(8, 1fr)",
          background: "#172033",
          color: colors.muted,
          fontSize: 12,
          fontWeight: 700,
        }}
      >
        {tableHeader.map((h) => (
          <div key={h} style={{padding: "10px 8px", borderRight: "1px solid rgba(255,255,255,0.05)"}}>
            {h}
          </div>
        ))}
      </div>
      {tableRows.map((row) => {
        const hot = dipMonths.has(row[0]);
        return (
          <div
            key={row[0]}
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(8, 1fr)",
              background: hot ? `rgba(255,75,75,${0.18 * pulse})` : "transparent",
              color: hot ? "#FECACA" : colors.ink,
              fontSize: 15,
              fontWeight: hot ? 700 : 500,
            }}
          >
            {row.map((cell, i) => (
              <div
                key={`${row[0]}-${i}`}
                style={{
                  padding: "11px 8px",
                  borderTop: "1px solid rgba(255,255,255,0.05)",
                  borderRight: "1px solid rgba(255,255,255,0.04)",
                }}
              >
                {cell}
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
};

export const ManagerFigure: React.FC<{size?: number}> = ({size = 280}) => {
  const frame = useCurrentFrame();
  const tilt = interpolate(frame, [0, 40], [0, 1], {extrapolateRight: "clamp"});
  return (
    <svg width={size} height={size * 1.15} viewBox="0 0 240 280" fill="none">
      <ellipse cx="120" cy="258" rx="70" ry="12" fill="rgba(0,0,0,0.25)" />
      <rect x="58" y="168" width="124" height="78" rx="10" fill="#1E293B" />
      <rect x="70" y="180" width="100" height="52" rx="4" fill="#0B1220" />
      <rect x="78" y="188" width="18" height="6" fill="#EF4444" opacity={0.8 + tilt * 0.2} />
      <rect x="100" y="188" width="28" height="6" fill="#64748B" />
      <rect x="78" y="200" width="52" height="5" fill="#334155" />
      <rect x="78" y="210" width="40" height="5" fill="#334155" />
      <rect x="78" y="220" width="46" height="5" fill="#FF4B4B" />
      <circle cx="120" cy="78" r="28" fill="#CBD5E1" />
      <rect x="88" y="108" width="64" height="70" rx="18" fill="#94A3B8" />
      <rect x="72" y="124" width="18" height="46" rx="8" fill="#94A3B8" />
      <rect x="150" y="124" width="18" height="46" rx="8" fill="#94A3B8" />
    </svg>
  );
};
