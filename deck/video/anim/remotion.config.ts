import { Config } from "@remotion/cli/config";

// PNG frames: the h264 comes out as standard yuv420p (JPEG frames give full-range yuvj420p, which PowerPoint and
// some players refuse), tagged BT.709 so players show the same colours.
Config.setVideoImageFormat("png");
Config.setColorSpace("bt709");
Config.setConcurrency(4);
