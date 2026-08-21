import React from "react";
import {AbsoluteFill, interpolate, useCurrentFrame} from "remotion";
import {DashboardBody, StreamlitShell} from "../components/dashboard";
import {Background, BrandChip, CaptionBar, Headline, useEnter, useFade, fontFamily} from "../components/ui";
import {colors, LayoutMode} from "../theme";

export const Solution: React.FC<{mode: LayoutMode}> = ({mode}) => {
  const fade = useFade();
  const frame = useCurrentFrame();
  const portrait = mode === "portrait";
  const drop = interpolate(frame, [0, 12], [-70, 0], {extrapolateRight: "clamp"});
  const showDash = interpolate(frame, [14, 32], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const enter = useEnter(4);
  const shellW = portrait ? 980 : 1120;
  const shellH = portrait ? 720 : 540;
  return (
    <AbsoluteFill style={{opacity: fade}}>
      <Background mode={mode} />
      <BrandChip mode={mode} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", paddingTop: portrait ? 220 : 160}}>
        <div
          style={{
            opacity: enter,
            transform: `scale(${0.94 + enter * 0.06})`,
            position: "relative",
            width: shellW,
            height: shellH,
          }}
        >
          <div style={{opacity: showDash}}>
            <StreamlitShell width={shellW} height={shellH} tab="Дашборд KPI">
              <DashboardBody />
            </StreamlitShell>
          </div>
          <div
            style={{
              position: "absolute",
              inset: 0,
              opacity: 1 - showDash,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 16,
              border: "2px dashed rgba(255,75,75,0.7)",
              borderRadius: 24,
              background: "rgba(11,18,32,0.92)",
              color: colors.ink,
              fontFamily,
            }}
          >
            <div
              style={{
                transform: `translateY(${drop}px)`,
                background: colors.paper,
                color: colors.streamlitText,
                borderRadius: 12,
                padding: "14px 22px",
                fontWeight: 800,
                boxShadow: "0 12px 30px rgba(0,0,0,0.25)",
              }}
            >
              📄 sample_data.csv
            </div>
            <div style={{fontSize: portrait ? 36 : 30, fontWeight: 800}}>Загрузить CSV</div>
            <div style={{color: colors.muted, fontSize: 18}}>или URL Google Sheets</div>
          </div>
        </div>
      </AbsoluteFill>
      <Headline mode={mode} delay={8}>
        Загрузите таблицу — получите понятную картину бизнеса
      </Headline>
      <CaptionBar
        mode={mode}
        delay={10}
        text="Загрузите таблицу — и получите понятную картину бизнеса"
      />
    </AbsoluteFill>
  );
};

export const Metrics: React.FC<{mode: LayoutMode}> = ({mode}) => {
  const fade = useFade();
  const portrait = mode === "portrait";
  return (
    <AbsoluteFill style={{opacity: fade}}>
      <Background mode={mode} />
      <BrandChip mode={mode} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", paddingTop: portrait ? 200 : 140}}>
        <StreamlitShell
          width={portrait ? 980 : 1180}
          height={portrait ? 760 : 560}
          tab="Дашборд KPI"
        >
          <DashboardBody highlightLtv />
        </StreamlitShell>
      </AbsoluteFill>
      <Headline mode={mode} delay={6}>
        Проблемы видны сразу
      </Headline>
      <CaptionBar
        mode={mode}
        delay={8}
        text="Падение ценности клиента видно сразу"
      />
    </AbsoluteFill>
  );
};
