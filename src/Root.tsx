import React from "react";
import { Composition } from "remotion";
import { ReelComposition } from "./ReelComposition";
import { BeatData, BEAT_DURATION_IN_FRAMES } from "./Beat";
import { getTotalFrames } from "./transitionPlan";
import beatsData from "./beats.json";

const FPS = 30;
const WIDTH = 1080;
const HEIGHT = 1920;
const TOTAL_FRAMES = getTotalFrames(
  beatsData as BeatData[],
  BEAT_DURATION_IN_FRAMES
);

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="Reel"
        component={ReelComposition}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
