import type { CSSProperties } from "react";
import { interpolate, random } from "remotion";

export const MOTION_DURATION_IN_FRAMES = 15;

const zoomIn = (frame: number): CSSProperties => {
  const scale = interpolate(frame, [0, MOTION_DURATION_IN_FRAMES], [1, 1.15], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return { transform: `scale(${scale})` };
};

const panLeft = (frame: number): CSSProperties => {
  const translateX = interpolate(
    frame,
    [0, MOTION_DURATION_IN_FRAMES],
    [4, -4],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  // Slight extra scale so the pan never reveals an edge of the frame.
  return { transform: `scale(1.1) translateX(${translateX}%)` };
};

const shake = (frame: number, seed: number): CSSProperties => {
  const damp = interpolate(frame, [0, MOTION_DURATION_IN_FRAMES], [1, 0.35], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const x = (random(`shake-x-${seed}-${frame}`) - 0.5) * 20 * damp;
  const y = (random(`shake-y-${seed}-${frame}`) - 0.5) * 20 * damp;
  return { transform: `translate(${x}px, ${y}px)` };
};

const tilt = (frame: number): CSSProperties => {
  const rotate = interpolate(frame, [0, MOTION_DURATION_IN_FRAMES], [-3, 3], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return { transform: `rotate(${rotate}deg) scale(1.05)` };
};

const MOTIONS: Record<string, (frame: number, seed: number) => CSSProperties> = {
  "zoom-in": (frame) => zoomIn(frame),
  "pan-left": (frame) => panLeft(frame),
  shake: (frame, seed) => shake(frame, seed),
  tilt: (frame) => tilt(frame),
};

export const getMotionStyle = (
  motion: string,
  frame: number,
  seed: number
): CSSProperties => {
  const fn = MOTIONS[motion] ?? MOTIONS["zoom-in"];
  return fn(frame, seed);
};
