export const colors = {
  canvas: "#0B1220",
  canvasAlt: "#111B2E",
  ink: "#F8FAFC",
  muted: "#94A3B8",
  streamlit: "#FF4B4B",
  streamlitDark: "#BD4043",
  plotly: "#636EFA",
  plotlyRed: "#EF553B",
  success: "#09AB3B",
  danger: "#FF4B4B",
  paper: "#FFFFFF",
  paperMuted: "#F0F2F6",
  streamlitText: "#31333F",
  streamlitSub: "#808495",
  anomaly: "#FFCCCC",
  telegram: "#229ED9",
  telegramDark: "#1B8BBF",
  card: "#162033",
  line: "rgba(255,255,255,0.08)",
};

export const timing = {
  fps: 30,
  durationSec: 35,
  scenes: {
    hook: {from: 0, duration: 5},
    problem: {from: 5, duration: 6.1},
    solution: {from: 11.1, duration: 4.5},
    metrics: {from: 15.6, duration: 5.4},
    analyst: {from: 21, duration: 4.3},
    telegram: {from: 25.3, duration: 4.6},
    offer: {from: 29.9, duration: 5.1},
  },
};

export const toFrames = (seconds: number, fps = timing.fps) =>
  Math.round(seconds * fps);

export type LayoutMode = "landscape" | "portrait";
