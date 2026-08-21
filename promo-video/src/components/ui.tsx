import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {colors, LayoutMode} from "../theme";

export const fontFamily = "Manrope, Inter, system-ui, sans-serif";

export const useFade = (inFrames = 8) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [0, inFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

export const useEnter = (delay = 0, stiffness = 120) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({
    frame: frame - delay,
    fps,
    config: {damping: 16, stiffness, mass: 0.7},
  });
};

export const Background: React.FC<{mode: LayoutMode}> = ({mode}) => {
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(1200px 700px at ${mode === "portrait" ? "50% 18%" : "18% 12%"}, #1A2744 0%, ${colors.canvas} 55%)`,
      }}
    >
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
          opacity: 0.45,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 88% 88%, rgba(255,75,75,0.18), transparent 32%)",
        }}
      />
    </AbsoluteFill>
  );
};

export const PulseMark: React.FC<{size?: number}> = ({size = 54}) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none">
    <rect width="64" height="64" rx="16" fill={colors.streamlit} />
    <path
      d="M10 34h8l4-12 8 24 6-16 4 8h14"
      stroke="white"
      strokeWidth="4"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const Headline: React.FC<{
  children: React.ReactNode;
  mode: LayoutMode;
  delay?: number;
}> = ({children, mode, delay = 6}) => {
  const enter = useEnter(delay);
  const size = mode === "portrait" ? 52 : 58;
  return (
    <div
      style={{
        position: "absolute",
        top: mode === "portrait" ? 118 : 78,
        left: 0,
        right: 0,
        zIndex: 6,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          transform: `translateY(${(1 - enter) * 28}px)`,
          opacity: enter,
          color: colors.ink,
          fontSize: size,
          fontWeight: 800,
          lineHeight: 1.18,
          letterSpacing: "-0.03em",
          textAlign: "center",
          maxWidth: mode === "portrait" ? 920 : 1500,
          padding: "12px 28px",
          textShadow: "0 10px 28px rgba(0,0,0,0.55)",
          fontFamily,
          background: "rgba(11,18,32,0.55)",
          borderRadius: 18,
        }}
      >
        {children}
      </div>
    </div>
  );
};

export const CaptionBar: React.FC<{
  text: string;
  mode: LayoutMode;
  delay?: number;
}> = ({text, mode, delay = 12}) => {
  const enter = useEnter(delay, 110);
  return (
    <div
      style={{
        position: "absolute",
        zIndex: 8,
        left: mode === "portrait" ? 48 : 80,
        right: mode === "portrait" ? 48 : 80,
        bottom: mode === "portrait" ? 72 : 48,
        display: "flex",
        justifyContent: "center",
        opacity: enter,
        transform: `translateY(${(1 - enter) * 16}px)`,
      }}
    >
      <div
        style={{
          background: "rgba(8,12,22,0.82)",
          border: "1px solid rgba(255,255,255,0.12)",
          color: colors.ink,
          fontSize: mode === "portrait" ? 40 : 36,
          fontWeight: 700,
          lineHeight: 1.25,
          padding: mode === "portrait" ? "18px 28px" : "14px 28px",
          borderRadius: 18,
          textAlign: "center",
          maxWidth: "100%",
          backdropFilter: "blur(10px)",
          fontFamily,
        }}
      >
        {text}
      </div>
    </div>
  );
};

export const BrandChip: React.FC<{mode: LayoutMode}> = ({mode}) => (
  <div
    style={{
      position: "absolute",
      top: mode === "portrait" ? 56 : 36,
      left: mode === "portrait" ? 48 : 48,
      display: "flex",
      alignItems: "center",
      gap: 12,
      color: colors.ink,
      fontWeight: 700,
      fontSize: 22,
      fontFamily,
    }}
  >
    <PulseMark size={36} />
    KPI Pulse
  </div>
);
