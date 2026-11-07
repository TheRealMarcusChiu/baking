// Open the recipe for #recipe links, keep print complete, and tilt the hero photo with the pointer.
const recipe = document.querySelector(".recipe-toggle");
const openForHash = () => {
  if (location.hash !== "#recipe") return;
  recipe.open = true;
  document.getElementById("recipe").scrollIntoView();
};
openForHash();
addEventListener("hashchange", openForHash);

let openBeforePrint = false;
addEventListener("beforeprint", () => { openBeforePrint = recipe.open; recipe.open = true; });
addEventListener("afterprint", () => { recipe.open = openBeforePrint; });

const img = document.querySelector(".hero img");
const reduced = matchMedia("(prefers-reduced-motion: reduce)");
const finePointer = matchMedia("(hover: hover) and (pointer: fine)");
let x = 0, y = 0, targetX = 0, targetY = 0, frameId = 0, visible = false;
const clamp = v => Math.max(-1, Math.min(1, v));

function frame() {
  frameId = 0;
  x += (targetX - x) * 0.14;
  y += (targetY - y) * 0.14;
  if (Math.abs(targetX - x) + Math.abs(targetY - y) < 0.002) { x = targetX; y = targetY; } else request();
  img.style.transform = x || y
    ? `perspective(1000px) rotateX(${(-y * 6).toFixed(3)}deg) rotateY(${(x * 6).toFixed(3)}deg) translate(${(x * 12).toFixed(2)}px, ${(y * 12).toFixed(2)}px)`
    : "";
}
function request() {
  if (!frameId && visible && !document.hidden) frameId = requestAnimationFrame(frame);
}
function aim(a, b) { targetX = a; targetY = b; request(); }
function rest() {
  cancelAnimationFrame(frameId);
  frameId = 0; x = y = targetX = targetY = 0;
  img.style.transform = "";
}

function start() {
  addEventListener("pointermove", e => {
    if (e.pointerType === "touch" || !finePointer.matches || reduced.matches) return;
    aim(clamp(e.clientX / innerWidth * 2 - 1), clamp(e.clientY / innerHeight * 2 - 1));
  }, { passive: true });
  document.documentElement.addEventListener("pointerleave", () => aim(0, 0));
  addEventListener("blur", () => aim(0, 0));
  document.addEventListener("visibilitychange", () => { if (document.hidden) rest(); });
  reduced.addEventListener("change", rest);
  finePointer.addEventListener("change", rest);
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    if (!visible) rest();
  }).observe(img);
}
// The photo shows first; motion only starts a frame after it has loaded.
const afterPhoto = () => requestAnimationFrame(start);
if (img.complete) afterPhoto(); else img.addEventListener("load", afterPhoto, { once: true });
