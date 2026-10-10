import { Config } from "@remotion/cli/config";

// PNG frames: the h264 comes out as standard yuv420p (JPEG frames give full-range yuvj420p, which PowerPoint and
// some players refuse), tagged BT.709 so players show the same colours.
Config.setVideoImageFormat("png");
Config.setColorSpace("bt709");
Config.setConcurrency(4);
// A keyframe every second (30 frames): pausing or scrubbing in PowerPoint then always shows a clean frame
// (with ~8 s between keyframes it could draw a new frame over a stale one).
Config.overrideFfmpegCommand(({ args }) => {
  if (!args.includes("libx264")) return args;
  return [...args.slice(0, -1), "-g", "30", "-keyint_min", "30", args[args.length - 1]];
});
