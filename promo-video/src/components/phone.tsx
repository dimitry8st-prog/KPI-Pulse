import React from "react";
import {digestLines} from "../data";
import {fontFamily} from "./ui";

export const PhoneDigest: React.FC<{width?: number; height?: number; progress?: number}> = ({
  width = 360,
  height = 720,
  progress = 1,
}) => {
  const lines = digestLines.slice(0, Math.max(3, Math.round(digestLines.length * progress)));
  return (
    <div
      style={{
        width,
        height,
        borderRadius: 42,
        background: "#0A0A0A",
        padding: 10,
        boxShadow: "0 30px 80px rgba(0,0,0,0.45)",
        fontFamily,
      }}
    >
      <div
        style={{
          height: "100%",
          borderRadius: 34,
          background: "#17212B",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div
          style={{
            height: 54,
            background: "#232E3C",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 18px",
            color: "white",
            fontWeight: 700,
          }}
        >
          <span style={{fontSize: 20}}>‹</span>
          <span>KPI Pulse</span>
          <span style={{width: 20}} />
        </div>
        <div style={{padding: 16, display: "flex", flexDirection: "column", gap: 10, flex: 1}}>
          <div style={{alignSelf: "center", color: "#6A7A88", fontSize: 12}}>сегодня · 09:00</div>
          <div
            style={{
              alignSelf: "flex-start",
              background: "#182533",
              borderRadius: 16,
              padding: 14,
              color: "white",
              fontSize: 14,
              lineHeight: 1.35,
              maxWidth: "100%",
              border: "1px solid rgba(255,255,255,0.04)",
            }}
          >
            {lines.map((line, i) => (
              <div key={i} style={{minHeight: line ? undefined : 8, fontWeight: line.startsWith("📊") ? 800 : 500}}>
                {line}
              </div>
            ))}
          </div>
        </div>
        <div
          style={{
            height: 48,
            background: "#232E3C",
            color: "#8B9AA8",
            display: "flex",
            alignItems: "center",
            padding: "0 16px",
            fontSize: 13,
          }}
        >
          /digest
        </div>
      </div>
    </div>
  );
};
