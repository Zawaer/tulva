import React from "react";
import { OffthreadVideo, Sequence, staticFile } from "remotion";
import clips from "../clips.json";
import { C, FPS, mix, ramp, word } from "../theme";

// Beat 2: the real web app (record_clips.mjs). Scroll to the March snow outlook, click "High snow", then zoom into
// the North tile while the voice says "from two to six point four percent".
const CLIP = clips.app_snow;
const [VW, VH] = CLIP.viewport;
const WIN = { x: 192, y: 24, w: 1536, bar: 36 };
const WIN_H = (WIN.w * VH) / VW; // 864
const S = WIN.w / VW;            // CSS px -> screen px at zoom 1
const tile = CLIP.north_tile;
// rows of the North tile (CSS px, measured on the recording): big number, "Tulva, no outlook", "Tulva + snow"
const NUM = { x: tile.x + 18, y: tile.y + 82, w: 124, h: 56 };
const ROW_NO = { x: tile.x + 12, y: tile.y + 170, w: tile.w - 24, h: 26 };
const ROW_SNOW = { x: tile.x + 12, y: tile.y + 197, w: tile.w - 24, h: 26 };

export const AppScene: React.FC<{ t: number }> = ({ t }) => {
  const zoom = ramp(t, CLIP.cues.click + 0.45, CLIP.cues.click + 1.4);
  const z = mix(1, 1.62, zoom);
  // focus: page centre -> North tile, clamped so the view never leaves the page
  const fx = mix(VW / 2, tile.x + tile.w / 2, zoom), fy = mix(VH / 2, tile.y + tile.h / 2 - 10, zoom);
  const cx = Math.min(Math.max(fx, VW / 2 / z), VW - VW / 2 / z);
  const cy = Math.min(Math.max(fy, VH / 2 / z), VH - VH / 2 / z);
  const tTwo = word(2, "two"), tSix = word(2, "six");
  const hlNo = ramp(t, tTwo - 0.1, tTwo + 0.15) * (1 - ramp(t, tSix - 0.1, tSix + 0.1));
  const hlSnow = ramp(t, tSix - 0.1, tSix + 0.15);
  const ring = ramp(t, tSix, tSix + 0.5);
  const box = (r: typeof NUM, op: number, style: React.CSSProperties) => (
    <div style={{ position: "absolute", left: r.x - 4, top: r.y - 3, width: r.w + 8, height: r.h + 6, borderRadius: 7,
      opacity: op, ...style }} />
  );
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", left: WIN.x, top: WIN.y, width: WIN.w, height: WIN.bar + WIN_H, borderRadius: 14,
        overflow: "hidden", background: "#fff", boxShadow: "0 30px 80px rgba(0,0,0,.45), 0 0 0 1px rgba(255,255,255,.08)" }}>
        <div style={{ height: WIN.bar, background: "#e9edf2", display: "flex", alignItems: "center", padding: "0 16px",
          gap: 8, position: "relative", borderBottom: "1px solid #d6dce4" }}>
          {["#ff5f57", "#febc2e", "#28c840"].map((c) => <div key={c} style={{ width: 13, height: 13, borderRadius: 7, background: c }} />)}
          <div style={{ position: "absolute", left: 0, right: 0, textAlign: "center", fontSize: 17, color: "#5d6b7e", fontWeight: 500 }}>
            Tulva web app · live recording
          </div>
        </div>
        <div style={{ position: "relative", width: WIN.w, height: WIN_H, overflow: "hidden", background: "#f5f8fb" }}>
          <div style={{ position: "absolute", left: 0, top: 0, width: VW, height: VH, transformOrigin: "0 0",
            transform: `translate(${WIN.w / 2}px, ${WIN_H / 2}px) scale(${S * z}) translate(${-cx}px, ${-cy}px)` }}>
            <Sequence from={Math.round(CLIP.start * FPS)} layout="none">
              <OffthreadVideo src={staticFile(CLIP.file)} muted style={{ width: VW, height: VH, display: "block" }} />
            </Sequence>
            {box(ROW_NO, hlNo, { background: "#cfe3ff", mixBlendMode: "multiply" })}
            {box(ROW_SNOW, hlSnow, { background: "#cfe3ff", mixBlendMode: "multiply" })}
            {box(NUM, ring, { border: `2.5px solid ${C.red}`, transform: `scale(${mix(1.25, 1, ring)})` })}
          </div>
        </div>
      </div>
    </div>
  );
};
