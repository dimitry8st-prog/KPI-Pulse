import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useVideoConfig,
} from "remotion";
import {Analyst, CoverStill, Offer, TelegramScene} from "./scenes/AnalystOffer";
import {Hook, Problem} from "./scenes/HookProblem";
import {Metrics, Solution} from "./scenes/SolutionMetrics";
import {LayoutMode, timing, toFrames} from "./theme";

export type PromoProps = {
  withVoiceover: boolean;
  withMusic: boolean;
};

const sceneFrames = {
  hook: toFrames(timing.scenes.hook.duration),
  problem: toFrames(timing.scenes.problem.duration),
  solution: toFrames(timing.scenes.solution.duration),
  metrics: toFrames(timing.scenes.metrics.duration),
  analyst: toFrames(timing.scenes.analyst.duration),
  telegram: toFrames(timing.scenes.telegram.duration),
  offer: toFrames(timing.scenes.offer.duration),
};

const starts = {
  hook: toFrames(timing.scenes.hook.from),
  problem: toFrames(timing.scenes.problem.from),
  solution: toFrames(timing.scenes.solution.from),
  metrics: toFrames(timing.scenes.metrics.from),
  analyst: toFrames(timing.scenes.analyst.from),
  telegram: toFrames(timing.scenes.telegram.from),
  offer: toFrames(timing.scenes.offer.from),
};

const overlap = 12;

export const Promo: React.FC<PromoProps & {mode: LayoutMode}> = ({
  withVoiceover,
  withMusic,
  mode,
}) => {
  const {fps} = useVideoConfig();
  const hold = (frames: number, isLast: boolean) => frames + (isLast ? 0 : overlap);
  return (
    <AbsoluteFill style={{background: "#0B1220"}}>
      <Sequence from={starts.hook} durationInFrames={hold(sceneFrames.hook, false)} name="Hook">
        <Hook mode={mode} />
      </Sequence>
      <Sequence from={starts.problem} durationInFrames={hold(sceneFrames.problem, false)} name="Problem">
        <Problem mode={mode} />
      </Sequence>
      <Sequence from={starts.solution} durationInFrames={hold(sceneFrames.solution, false)} name="Solution">
        <Solution mode={mode} />
      </Sequence>
      <Sequence from={starts.metrics} durationInFrames={hold(sceneFrames.metrics, false)} name="Metrics">
        <Metrics mode={mode} />
      </Sequence>
      <Sequence from={starts.analyst} durationInFrames={hold(sceneFrames.analyst, false)} name="Analyst">
        <Analyst mode={mode} />
      </Sequence>
      <Sequence from={starts.telegram} durationInFrames={hold(sceneFrames.telegram, false)} name="Telegram">
        <TelegramScene mode={mode} />
      </Sequence>
      <Sequence from={starts.offer} durationInFrames={hold(sceneFrames.offer, true)} name="Offer">
        <Offer mode={mode} />
      </Sequence>
      {withMusic ? (
        <Audio src={staticFile("music/kpi-pulse-bed.wav")} volume={withVoiceover ? 0.12 : 0.28} />
      ) : null}
      {withVoiceover ? (
        <>
          <Sequence from={starts.hook} durationInFrames={sceneFrames.hook}>
            <Audio src={staticFile("voiceover/hook.mp3")} volume={1} />
          </Sequence>
          <Sequence from={starts.problem} durationInFrames={sceneFrames.problem}>
            <Audio src={staticFile("voiceover/problem.mp3")} volume={1} />
          </Sequence>
          <Sequence from={starts.solution} durationInFrames={sceneFrames.solution}>
            <Audio src={staticFile("voiceover/solution.mp3")} volume={1} />
          </Sequence>
          <Sequence from={starts.metrics} durationInFrames={sceneFrames.metrics}>
            <Audio src={staticFile("voiceover/metrics.mp3")} volume={1} />
          </Sequence>
          <Sequence from={starts.analyst} durationInFrames={sceneFrames.analyst}>
            <Audio src={staticFile("voiceover/analyst.mp3")} volume={1} />
          </Sequence>
          <Sequence from={starts.telegram} durationInFrames={sceneFrames.telegram}>
            <Audio src={staticFile("voiceover/telegram.mp3")} volume={1} />
          </Sequence>
          <Sequence from={starts.offer} durationInFrames={sceneFrames.offer}>
            <Audio src={staticFile("voiceover/offer.mp3")} volume={1} />
          </Sequence>
        </>
      ) : null}
      <span style={{display: "none"}}>{fps}</span>
    </AbsoluteFill>
  );
};

export const LandscapePromo: React.FC<PromoProps> = (props) => (
  <Promo {...props} mode="landscape" />
);

export const PortraitPromo: React.FC<PromoProps> = (props) => (
  <Promo {...props} mode="portrait" />
);

export {CoverStill};
