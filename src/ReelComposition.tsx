import React from "react";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { Beat, BeatData, BEAT_DURATION_IN_FRAMES } from "./Beat";
import { getBeatDurations, getTransitionDuration } from "./transitionPlan";
import { whip } from "./transitions/whip";
import { glitch } from "./transitions/glitch";
import beatsData from "./beats.json";

const beats = beatsData as BeatData[];
const beatDurations = getBeatDurations(beats, BEAT_DURATION_IN_FRAMES);

const getPresentation = (transition: string) => {
  switch (transition) {
    case "whip":
      return whip();
    case "glitch":
      return glitch();
    default:
      return null;
  }
};

export const ReelComposition: React.FC = () => {
  return (
    <TransitionSeries>
      {beats.flatMap((beat, index) => {
        const elements: React.ReactNode[] = [];

        if (index > 0) {
          const duration = getTransitionDuration(beat.transition);
          const presentation = getPresentation(beat.transition);

          // "cut" (or any transition with 0 duration) is just a hard cut:
          // no <TransitionSeries.Transition> needed, beats simply play back to back.
          if (presentation && duration > 0) {
            elements.push(
              <TransitionSeries.Transition
                key={`transition-${beat.id}`}
                presentation={presentation}
                timing={linearTiming({ durationInFrames: duration })}
              />
            );
          }
        }

        elements.push(
          <TransitionSeries.Sequence
            key={`beat-${beat.id}`}
            durationInFrames={beatDurations[index]}
          >
            <Beat beat={beat} />
          </TransitionSeries.Sequence>
        );

        return elements;
      })}
    </TransitionSeries>
  );
};
