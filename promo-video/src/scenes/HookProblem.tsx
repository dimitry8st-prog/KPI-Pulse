import React from "react";
import {AbsoluteFill, interpolate, useCurrentFrame} from "remotion";
import {Background, BrandChip, CaptionBar, Headline, useEnter, useFade} from "../components/ui";
import {ManagerFigure, Spreadsheet} from "../components/spreadsheet";
import {LayoutMode} from "../theme";

export const Hook: React.FC<{mode: LayoutMode}> = ({mode}) => {
  const fade = useFade();
  const frame = useCurrentFrame();
  const shift = interpolate(frame, [0, 120], [0, -18], {extrapolateRight: "clamp"});
  const portrait = mode === "portrait";
  return (
    <AbsoluteFill style={{opacity: fade}}>
      <Background mode={mode} />
      <BrandChip mode={mode} />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: portrait ? "flex-start" : "center",
          paddingTop: portrait ? 180 : 0,
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: portrait ? "column" : "row",
            alignItems: "center",
            gap: portrait ? 28 : 48,
            transform: `translateY(${shift}px)`,
          }}
        >
          <ManagerFigure size={portrait ? 300 : 260} />
          <Spreadsheet width={portrait ? 920 : 920} height={portrait ? 420 : 340} />
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{justifyContent: "center", alignItems: "center", paddingBottom: portrait ? 120 : 40}}>
        <Headline mode={mode}>Цифры есть. А что происходит с бизнесом?</Headline>
      </AbsoluteFill>
      <CaptionBar
        mode={mode}
        text="Отчёты полны цифр. А что делать с бизнесом — неясно"
      />
    </AbsoluteFill>
  );
};

const Pill: React.FC<{text: string; delay: number; portrait: boolean}> = ({
  text,
  delay,
  portrait,
}) => {
  const enter = useEnter(delay, 140);
  return (
    <div
      style={{
        opacity: enter,
        transform: `translateY(${(1 - enter) * 18}px)`,
        background: "#FF4B4B",
        color: "white",
        fontWeight: 800,
        fontSize: portrait ? 28 : 24,
        padding: "10px 18px",
        borderRadius: 999,
      }}
    >
      {text}
    </div>
  );
};

export const Problem: React.FC<{mode: LayoutMode}> = ({mode}) => {
  const fade = useFade();
  const pills = ["Выручка", "Расходы", "Клиенты", "Конверсия"];
  const portrait = mode === "portrait";
  return (
    <AbsoluteFill style={{opacity: fade}}>
      <Background mode={mode} />
      <BrandChip mode={mode} />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          paddingTop: portrait ? 80 : 20,
        }}
      >
        <Spreadsheet width={portrait ? 960 : 1280} height={portrait ? 520 : 430} glow />
      </AbsoluteFill>
      <div
        style={{
          position: "absolute",
          top: portrait ? 150 : 110,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          gap: 12,
          flexWrap: "wrap",
          padding: "0 40px",
        }}
      >
        {pills.map((pill, i) => (
          <Pill key={pill} text={pill} delay={4 + i * 5} portrait={portrait} />
        ))}
      </div>
      <CaptionBar mode={mode} delay={8} text="Искать вручную — значит опоздать" />
    </AbsoluteFill>
  );
};
