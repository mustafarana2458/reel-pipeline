import type { BeatData } from "./Beat";

// "cut" costs no frames (it's just a hard cut, no overlap).
// "whip" and "glitch" overlap the adjacent beats for their duration.
// Keep these even numbers -- getBeatDurations() splits them in half per
// neighboring beat, and integer durationInFrames is required.
export const TRANSITION_DURATIONS: Record<string, number> = {
  cut: 0,
  whip: 6,
  glitch: 8,
};

export const getTransitionDuration = (transition: string): number =>
  TRANSITION_DURATIONS[transition] ?? 0;

// beat.transition describes how that beat enters (the transition from the
// previous beat into this one). The first beat has no incoming transition.
//
// A <TransitionSeries.Transition> of duration D overlaps the tail of the
// previous beat's Sequence with the head of this beat's Sequence, which
// would otherwise shrink the video's total length. To keep every beat's
// "own" screen time at a full baseDuration and the overall video at exactly
// beats.length * baseDuration, each beat's Sequence is padded by half of its
// incoming transition and half of its outgoing transition -- that padding
// is exactly what the neighboring <Transition> subtracts back out.
export const getBeatDurations = (
  beats: BeatData[],
  baseDuration: number
): number[] => {
  return beats.map((beat, index) => {
    const dLeft = index > 0 ? getTransitionDuration(beat.transition) : 0;
    const dRight =
      index < beats.length - 1
        ? getTransitionDuration(beats[index + 1].transition)
        : 0;
    return baseDuration + dLeft / 2 + dRight / 2;
  });
};

// The half/half padding above cancels out exactly against what each
// <Transition> subtracts, so the total is always just beats * baseDuration,
// regardless of which transitions are used.
export const getTotalFrames = (
  beats: BeatData[],
  baseDuration: number
): number => beats.length * baseDuration;
