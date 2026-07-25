import React from "react";
import { AbsoluteFill } from "remotion";
import type {
  TransitionPresentation,
  TransitionPresentationComponentProps,
} from "@remotion/transitions";

export type WhipProps = Record<string, never>;

const WhipPresentation: React.FC<
  TransitionPresentationComponentProps<WhipProps>
> = ({ children, presentationProgress, presentationDirection }) => {
  const isEntering = presentationDirection === "entering";

  // Exiting scene whips out to the left, entering scene whips in from the right.
  const translateX = isEntering
    ? (1 - presentationProgress) * 130
    : -presentationProgress * 130;

  const blur = isEntering
    ? (1 - presentationProgress) * 18
    : presentationProgress * 18;

  const skew = isEntering
    ? (1 - presentationProgress) * 6
    : -presentationProgress * 6;

  return (
    <AbsoluteFill
      style={{
        transform: `translateX(${translateX}%) skewX(${skew}deg)`,
        filter: `blur(${blur}px)`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

export const whip = (): TransitionPresentation<WhipProps> => ({
  component: WhipPresentation,
  props: {},
});
