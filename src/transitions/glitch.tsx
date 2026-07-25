import React from "react";
import { AbsoluteFill, random } from "remotion";
import type {
  TransitionPresentation,
  TransitionPresentationComponentProps,
} from "@remotion/transitions";

export type GlitchProps = Record<string, never>;

const STEPS = 10;

const GlitchPresentation: React.FC<
  TransitionPresentationComponentProps<GlitchProps>
> = ({ children, presentationProgress, presentationDirection }) => {
  const isEntering = presentationDirection === "entering";
  const opacity = isEntering
    ? presentationProgress
    : 1 - presentationProgress;

  // Quantize progress into steps so the jitter "stutters" instead of gliding smoothly.
  const step = Math.floor(presentationProgress * STEPS);
  const seedBase = `glitch-${presentationDirection}-${step}`;
  const jitterX = (random(`${seedBase}-x`) - 0.5) * 40;
  const jitterY = (random(`${seedBase}-y`) - 0.5) * 14;
  const sliceOffset = (random(`${seedBase}-slice`) - 0.5) * 30;

  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill style={{ transform: `translate(${jitterX}px, ${jitterY}px)` }}>
        {children}
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          transform: `translate(${jitterX + sliceOffset}px, ${jitterY}px)`,
          mixBlendMode: "screen",
          filter: "brightness(1.5) saturate(2) hue-rotate(-40deg)",
          opacity: 0.5,
        }}
      >
        {children}
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          transform: `translate(${jitterX - sliceOffset}px, ${jitterY}px)`,
          mixBlendMode: "screen",
          filter: "brightness(1.5) saturate(2) hue-rotate(160deg)",
          opacity: 0.5,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const glitch = (): TransitionPresentation<GlitchProps> => ({
  component: GlitchPresentation,
  props: {},
});
