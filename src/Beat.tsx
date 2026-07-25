import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { getMotionStyle } from "./motions";

export const BEAT_DURATION_IN_FRAMES = 15;

export type BeatData = {
  id: number;
  text: string;
  image: string;
  motion: string;
  transition: string;
};

const PLACEHOLDER_COLORS = [
  "#1f2937",
  "#7c2d12",
  "#14532d",
  "#312e81",
  "#701a75",
];

export const Beat: React.FC<{ beat: BeatData }> = ({ beat }) => {
  const frame = useCurrentFrame();

  const motionStyle = getMotionStyle(beat.motion, frame, beat.id);

  const opacity = interpolate(
    frame,
    [0, 4],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const backgroundColor =
    PLACEHOLDER_COLORS[beat.id % PLACEHOLDER_COLORS.length];

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          backgroundColor,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          ...motionStyle,
        }}
      >
        <p
          style={{
            color: "white",
            fontSize: 64,
            fontWeight: 700,
            textAlign: "center",
            fontFamily: "sans-serif",
            padding: "0 80px",
            opacity,
          }}
        >
          {beat.text}
        </p>
      </div>
    </AbsoluteFill>
  );
};
