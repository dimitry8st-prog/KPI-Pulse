import React from "react";
import {AbsoluteFill, interpolate, useCurrentFrame} from "remotion";
import {StreamlitShell} from "../components/dashboard";
import {PhoneDigest} from "../components/phone";
import {Background, BrandChip, CaptionBar, Headline, PulseMark, useEnter, useFade, fontFamily} from "../components/ui";
import {aiAnswer, aiQuestion} from "../data";
import {colors, LayoutMode} from "../theme";

export const Analyst: React.FC<{mode: LayoutMode}> = ({mode}) => {
  const fade = useFade();
  const frame = useCurrentFrame();
  const portrait = mode === "portrait";
  const typed = Math.floor(
    interpolate(frame, [4, 32], [0, aiQuestion.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const answerOpacity = interpolate(frame, [34, 48], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{opacity: fade}}>
      <Background mode={mode} />
      <BrandChip mode={mode} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center", paddingTop: portrait ? 200 : 140}}>
        <StreamlitShell
          width={portrait ? 980 : 1040}
          height={portrait ? 780 : 540}
          tab="AI-аналитик"
        >
          <div style={{fontFamily, color: colors.streamlitText}}>
            <div style={{fontSize: 22, fontWeight: 800, marginBottom: 14}}>🤖 AI-аналитик</div>
            <div
              style={{
                background: "#F0F2F6",
                borderRadius: 16,
                padding: 14,
                marginBottom: 12,
                maxWidth: "92%",
              }}
            >
              <div style={{fontSize: 13, color: colors.streamlitSub, marginBottom: 4}}>Вы</div>
              <div style={{fontSize: portrait ? 28 : 24, fontWeight: 700, minHeight: 36}}>
                {aiQuestion.slice(0, typed)}
                {typed < aiQuestion.length ? (
                  <span style={{opacity: frame % 16 < 8 ? 1 : 0}}>|</span>
                ) : null}
              </div>
            </div>
            <div
              style={{
                background: "#FFF5F5",
                border: `1px solid ${colors.streamlit}`,
                borderRadius: 16,
                padding: 16,
                opacity: answerOpacity,
                transform: `translateY(${(1 - answerOpacity) * 12}px)`,
                whiteSpace: "pre-wrap",
                fontSize: portrait ? 24 : 20,
                lineHeight: 1.35,
                fontWeight: 600,
              }}
            >
              <div style={{fontSize: 13, color: colors.streamlit, marginBottom: 6}}>AI-аналитик</div>
              {aiAnswer}
            </div>
          </div>
        </StreamlitShell>
      </AbsoluteFill>
      <Headline mode={mode} delay={4}>
        Спросите обычными словами
      </Headline>
      <CaptionBar
        mode={mode}
        delay={8}
        text="Спросите своими словами — получите причину и что делать"
      />
    </AbsoluteFill>
  );
};

export const TelegramScene: React.FC<{mode: LayoutMode}> = ({mode}) => {
  const fade = useFade();
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [4, 70], [0.35, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const portrait = mode === "portrait";
  return (
    <AbsoluteFill style={{opacity: fade}}>
      <Background mode={mode} />
      <BrandChip mode={mode} />
      <AbsoluteFill style={{alignItems: "center", justifyContent: "center"}}>
        <PhoneDigest
          width={portrait ? 460 : 400}
          height={portrait ? 920 : 760}
          progress={progress}
        />
      </AbsoluteFill>
      <Headline mode={mode}>Главные показатели всегда под рукой</Headline>
      <CaptionBar mode={mode} delay={6} text="Отчёт придёт в Telegram. Цифры всегда под рукой" />
    </AbsoluteFill>
  );
};

export const Offer: React.FC<{mode: LayoutMode}> = ({mode}) => {
  const fade = useFade();
  const enter = useEnter(4);
  const btn = useEnter(18);
  const portrait = mode === "portrait";
  return (
    <AbsoluteFill style={{opacity: fade}}>
      <Background mode={mode} />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          gap: 18,
          transform: `scale(${0.94 + enter * 0.06})`,
          opacity: enter,
        }}
      >
        <PulseMark size={portrait ? 92 : 78} />
        <div
          style={{
            color: "white",
            fontSize: portrait ? 64 : 62,
            fontWeight: 800,
            textAlign: "center",
            letterSpacing: "-0.04em",
            fontFamily,
            maxWidth: portrait ? 900 : 1400,
            lineHeight: 1.15,
            padding: "0 36px",
          }}
        >
          KPI Pulse — ваш AI-аналитик бизнеса
        </div>
        <div
          style={{
            color: colors.muted,
            fontSize: portrait ? 34 : 30,
            fontWeight: 700,
            textAlign: "center",
            maxWidth: 980,
            padding: "0 32px",
            fontFamily,
          }}
        >
          Меньше таблиц. Больше понятных решений
        </div>
        <div
          style={{
            marginTop: 10,
            opacity: btn,
            transform: `translateY(${(1 - btn) * 14}px)`,
            background: colors.streamlit,
            color: "white",
            fontWeight: 800,
            fontSize: portrait ? 32 : 28,
            padding: "16px 36px",
            borderRadius: 16,
            fontFamily,
            boxShadow: "0 12px 30px rgba(255,75,75,0.35)",
          }}
        >
          Попробовать KPI Pulse
        </div>
        <div style={{color: colors.ink, fontSize: portrait ? 24 : 22, fontWeight: 600, fontFamily}}>
          Демо-версия и внедрение под ваш бизнес
        </div>
        <div
          style={{
            position: "absolute",
            bottom: portrait ? 80 : 36,
            color: "rgba(255,255,255,0.42)",
            fontSize: 13,
            fontFamily,
            textAlign: "center",
            padding: "0 24px",
          }}
        >
          Python · Streamlit · Claude · ChromaDB · SQLite · Telegram
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const CoverStill: React.FC = () => {
  return (
    <AbsoluteFill>
      <Background mode="landscape" />
      <AbsoluteFill
        style={{
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "48px 64px",
        }}
      >
        <div style={{maxWidth: 620}}>
          <div style={{display: "flex", alignItems: "center", gap: 14, marginBottom: 18}}>
            <PulseMark size={56} />
            <span style={{color: "white", fontSize: 28, fontWeight: 800, fontFamily}}>KPI Pulse</span>
          </div>
          <div
            style={{
              color: "white",
              fontSize: 46,
              fontWeight: 800,
              lineHeight: 1.15,
              letterSpacing: "-0.03em",
              fontFamily,
            }}
          >
            Сложные таблицы — в понятные решения
          </div>
          <div style={{color: colors.muted, marginTop: 16, fontSize: 22, fontFamily, fontWeight: 600}}>
            AI-аналитик бизнеса для руководителей
          </div>
        </div>
        <div style={{transform: "scale(0.72)", transformOrigin: "right center"}}>
          <StreamlitShell width={980} height={540} tab="Дашборд KPI">
            <div style={{fontFamily, color: colors.streamlitText}}>
              <div style={{fontSize: 20, fontWeight: 800, marginBottom: 10}}>📊 Дашборд KPI</div>
              <div style={{display: "flex", gap: 8}}>
                {["MRR 345,000", "CAC 415", "LTV 4,016", "Churn 2.18%", "Conv 54.63%"].map((item) => (
                  <div
                    key={item}
                    style={{
                      background: colors.paperMuted,
                      borderRadius: 10,
                      padding: "10px 12px",
                      fontWeight: 800,
                      fontSize: 16,
                    }}
                  >
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </StreamlitShell>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
