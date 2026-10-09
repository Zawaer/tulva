import { Composition } from "remotion";
import { Demo } from "./Demo";
import { FPS, H, W } from "./theme";
import timing from "./timing.json";

export const Root = () => (
  <Composition id="TulvaDemo" component={Demo} durationInFrames={Math.ceil(timing.total * FPS)} fps={FPS}
    width={W} height={H} />
);
