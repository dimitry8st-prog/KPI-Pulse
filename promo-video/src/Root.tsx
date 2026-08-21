import React from "react";
import {Composition, Folder} from "remotion";
import {loadFont} from "@remotion/google-fonts/Manrope";
import {CoverStill, LandscapePromo, PortraitPromo, PromoProps} from "./Promo";
import {toFrames} from "./theme";

loadFont("normal", {
  weights: ["600", "700", "800"],
  subsets: ["cyrillic", "latin"],
  ignoreTooManyRequestsWarning: true,
});

const defaultProps: PromoProps = {
  withVoiceover: false,
  withMusic: true,
};

const duration = toFrames(35);

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="KPI-Pulse">
        <Composition
          id="KpiPulsePromo"
          component={LandscapePromo}
          durationInFrames={duration}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={defaultProps}
        />
        <Composition
          id="KpiPulsePromoVertical"
          component={PortraitPromo}
          durationInFrames={duration}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={defaultProps}
        />
        <Composition
          id="KpiPulseCover"
          component={CoverStill}
          durationInFrames={1}
          fps={30}
          width={1280}
          height={720}
        />
      </Folder>
    </>
  );
};
