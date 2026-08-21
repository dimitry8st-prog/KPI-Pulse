import React from "react";
import {interpolate, useCurrentFrame} from "remotion";
import {colors} from "../theme";
import {fontFamily} from "./ui";
import {monthly12} from "../data";

export const Sparkline: React.FC<{
  values: number[];
  width: number;
  height: number;
  color?: string;
  progress?: number;
}> = ({values, width, height, color = colors.plotly, progress = 1}) => {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const pad = 6;
  const pts = values.map((v, i) => {
    const x = pad + (i / (values.length - 1)) * (width - pad * 2);
    const y =
      height - pad - ((v - min) / (max - min || 1)) * (height - pad * 2);
    return `${x},${y}`;
  });
  const shown = Math.max(2, Math.round(pts.length * progress));
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="3.5"
        strokeLinejoin="round"
        strokeLinecap="round"
        points={pts.slice(0, shown).join(" ")}
      />
    </svg>
  );
};

export const StreamlitShell: React.FC<{
  width: number;
  height: number;
  tab: "Данные" | "Дашборд KPI" | "AI-аналитик";
  children: React.ReactNode;
}> = ({width, height, tab, children}) => {
  const tabs = ["Данные", "Дашборд KPI", "AI-аналитик", "Настройки"];
  return (
    <div
      style={{
        width,
        height,
        background: colors.paper,
        borderRadius: 18,
        overflow: "hidden",
        boxShadow: "0 30px 80px rgba(0,0,0,0.35)",
        color: colors.streamlitText,
        fontFamily,
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          height: 46,
          background: colors.paperMuted,
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "0 16px",
          borderBottom: "1px solid #E6EAF1",
        }}
      >
        <span style={{width: 10, height: 10, borderRadius: 99, background: "#FF5F57"}} />
        <span style={{width: 10, height: 10, borderRadius: 99, background: "#FEBB2E"}} />
        <span style={{width: 10, height: 10, borderRadius: 99, background: "#28C840"}} />
        <div style={{flex: 1, textAlign: "center", fontSize: 13, color: colors.streamlitSub}}>
          localhost:8501 — KPI Pulse
        </div>
      </div>
      <div style={{padding: "16px 22px 8px", fontSize: 26, fontWeight: 800}}>
        📈 KPI Pulse — AI-аналитика бизнес-метрик
      </div>
      <div
        style={{
          display: "flex",
          gap: 22,
          padding: "0 22px",
          borderBottom: "1px solid #E6EAF1",
        }}
      >
        {tabs.map((name) => (
          <div
            key={name}
            style={{
              padding: "10px 2px 12px",
              fontSize: 15,
              fontWeight: name === tab ? 700 : 500,
              color: name === tab ? colors.streamlit : colors.streamlitSub,
              borderBottom: name === tab ? `3px solid ${colors.streamlit}` : "3px solid transparent",
            }}
          >
            {name}
          </div>
        ))}
      </div>
      <div style={{flex: 1, padding: 18, overflow: "hidden"}}>{children}</div>
    </div>
  );
};

export const MetricCard: React.FC<{
  label: string;
  ru?: string;
  value: string;
  delta: string;
  positive: boolean;
  highlight?: boolean;
  width?: number;
}> = ({label, ru, value, delta, positive, highlight, width = 200}) => (
  <div
    style={{
      width,
      background: highlight ? "#FFF5F5" : colors.paperMuted,
      border: highlight ? `2px solid ${colors.streamlit}` : "1px solid #E6EAF1",
      borderRadius: 14,
      padding: "12px 14px",
      boxShadow: highlight ? `0 0 0 6px rgba(255,75,75,0.12)` : "none",
    }}
  >
    {ru ? (
      <div style={{fontSize: 12, fontWeight: 700, color: colors.streamlit, marginBottom: 2}}>
        {ru}
      </div>
    ) : null}
    <div style={{fontSize: 13, color: colors.streamlitSub, fontWeight: 600}}>{label}</div>
    <div style={{fontSize: 26, fontWeight: 800, letterSpacing: "-0.03em", marginTop: 4}}>
      {value}
    </div>
    <div
      style={{
        marginTop: 4,
        fontSize: 14,
        fontWeight: 700,
        color: positive ? colors.success : colors.danger,
      }}
    >
      {positive ? "▲" : "▼"} {delta.replace("+", "").replace("-", "")}
    </div>
  </div>
);

export const DashboardBody: React.FC<{highlightLtv?: boolean; chartProgress?: number}> = ({
  highlightLtv = false,
  chartProgress = 1,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, 28], [0, chartProgress], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cards = [
    {label: "MRR руб.", ru: "Выручка", value: "345,000.00", delta: "+2.07%", positive: true},
    {label: "CAC руб.", ru: "Стоимость привлечения", value: "415.38", delta: "+0.32%", positive: true},
    {
      label: "LTV руб.",
      ru: "Ценность клиента",
      value: "4,015.52",
      delta: "-2.24%",
      positive: false,
      highlight: highlightLtv,
    },
    {label: "Churn %", ru: "Отток", value: "2.18", delta: "-8.4%", positive: false},
    {label: "Conversion %", ru: "Конверсия", value: "54.63", delta: "+1.17%", positive: true},
  ];
  return (
    <div>
      <div style={{fontSize: 22, fontWeight: 800, marginBottom: 12}}>📊 Дашборд KPI</div>
      <div style={{display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap"}}>
        {cards.map((card) => (
          <MetricCard key={card.label} {...card} width={168} />
        ))}
      </div>
      <div
        style={{
          background: colors.paperMuted,
          borderRadius: 14,
          padding: 12,
        }}
      >
        <div style={{fontSize: 13, fontWeight: 700, marginBottom: 6, color: colors.streamlitSub}}>
          MRR по месяцам · тестовые данные sample_data.csv
        </div>
        <Sparkline values={monthly12.mrr} width={860} height={92} progress={progress} />
      </div>
    </div>
  );
};
