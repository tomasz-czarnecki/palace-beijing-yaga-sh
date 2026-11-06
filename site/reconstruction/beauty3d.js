// Round 23: Beautiful light for the 3D view, ported from the Küstrin project's beauty3d.js: a sun that follows a clear day over Beijing into the night, its shadows, a sky, haze over the Western Hills, water that takes the sky, tone mapping and a soft ambient occlusion. The night's lanterns are night3d.js; the shader's side of them is here.
// The Clean mode is the historical view; this one is a choice made for the look and says nothing about 1860: the day, the weather, the hour and every lantern are chosen, not read from a source.
// An ES module, fetched by 3d.js right behind the first frame (or when first switched on), so Clean costs nothing. Nothing global is touched: each material gets its patch through onBeforeCompile while the mode is on, and gets its old self back when it is off. The panel's preview has its own renderer and never sees any of it.
// No post-processing pass: the grade sits in the materials' tone mapping, the occlusion is a height map of the gardens baked once in the browser (blurred heights: what stands above a point shades it), and the haze is in each material's fog. So the picture stays on the screen's own antialiasing.
// Shadows: two cascades on two directional lights, the second with no light of its own; each is fitted to what the camera sees of the ground, snapped to its texels, and redrawn only when the view leaves it, the sun moves on, or new detail (the kit's and the planting's near tiles, a model) comes in. Hills, banks and the land beyond the walls cast and take shadow; flat things laid on the ground (paths, courts, patches, water) only take it.
// Halls have no normals (halls3d.js shades them flat from the screen's derivatives), so they can't take a normal bias: their shadow pass gets a depth material with a slope-scaled offset instead.
// The haze (aerial perspective): every patched material's fog is replaced by one that thins with height and turns from a blue-grey at middle distance to the sky's own horizon colour far off, so the Western Hills stand in soft layers and meet the sky without a seam. The horizon is the far plane's straight line under full haze: nothing bends it.
// URL (read by 3d.js): light=clean|sun, time=<clock hour, 0-24>, cycle=1 (the day plays from there), lightq=high|mid|low|min.
// To change the day: SEASONS (declination and the clock's noon per season of the view's Season selector; summer is the default), SUN_DEFAULT_HOUR, and the SKY table (colours by the sun's altitude).

const QUALITY = {
  high: { near: 4096, far: 2048, aoSource: 2048, ao: 1024, clouds: true },
  mid: { near: 2048, far: 2048, aoSource: 2048, ao: 1024, clouds: true },
  low: { near: 1536, far: 1024, aoSource: 1024, ao: 512, clouds: false },
  min: { near: 1024, far: 0, aoSource: 0, ao: 0, clouds: false, ratio: 1.25 }, // one cascade, no occlusion: what the slowest machine gets
};
const NEXT_DOWN = { high: "mid", mid: "low", low: "min" };
const STEP_DOWN_MS = 50; // a frame slower than this on the probe: the next quality down
const STEP_TO_MIN_MS = 80; // low is what a phone starts on: only a really slow one leaves it

// The sun over the gardens (40.0 N, 116.3 E) by Beijing's clock (UTC+8, so the sun stands highest about 15 minutes after twelve, more or less by the equation of time). A clear day in each season of the Season selector; summer, the default, is about 1 July: up at 04:50, highest at 12:19, down at 19:47. A choice, as the hour is.
const LATITUDE = 40.0;
export const SEASONS = {
  spring: { declination: 9.6, noon: 12.25, day: "15 April" },
  summer: { declination: 23.1, noon: 12.31, day: "1 July" },
  autumn: { declination: -8.6, noon: 12.01, day: "15 October" },
  winter: { declination: -21.1, noon: 12.4, day: "15 January" },
};
export const SUN_DEFAULT_HOUR = 18.5; // the golden hour of a summer's day: the sun about 12° up in the west-north-west, long warm shadows across the courts
export const SUN_HOURS = [0, 24];
// A full moon of that night: opposite the sun, so as high in the south at midnight as the sun is low at noon.
const LOW_SUN_DEG = 3; // the light itself stops sinking here, or the shadows run off the map; it fades out instead
const STEP_NEAR_DEG = [0.15, 0.5], STEP_NEAR_AT_M = 400, STEP_FAR_DEG = 1; // while the day plays, how far the light moves between redraws of a cascade: finer close up, where a step would show

const AO_BOX = [-1700, -1440, 1760, 1400]; // x0, z0, x1, z1: the ground's domain (generated/ground.json) and a margin
const AO_Y0 = -10, AO_RANGE = 80; // metres: what the bake's values mean, before the 2x option
const AO_STRENGTH = 0.7;
const CASTERS_TOP_M = [60, 1600]; // above the water: higher than any ridge in the gardens; for the far map, the Western Hills
const WATER = "vec3(0.159, 0.347, 0.434)"; // 0x6f9fb0 (GROUND_COLOURS.water, AROUND_COLOURS.water, canal) in linear: how the land's own vertex colours mark water
const PANE = "vec3(6.0, 8.0, 10.0)"; // KIT_COLOURS.pane 0x2b3137 as halls3d.js stores it: linear, a byte a channel. A hall's window, lit at night
// The haze: optical depth per metre at the ground, the height over which it thins, and how its colour turns from blue-grey to the horizon's.
const HAZE_PER_M = 1.05e-4, HAZE_HEIGHT_M = 1800;

const smooth = (a, b, x) => { const t = Math.min(Math.max((x - a) / (b - a), 0), 1); return t * t * (3 - 2 * t); };
const mix3 = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);

// Altitude in degrees, azimuth from south towards west, and the way to it: x east, z south.
function skyPoint(hour, noon, declination) {
  const phi = (LATITUDE * Math.PI) / 180, dec = (declination * Math.PI) / 180, H = ((hour - noon) * 15 * Math.PI) / 180;
  const alt = Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(H));
  const az = Math.atan2(Math.sin(H), Math.cos(H) * Math.sin(phi) - Math.tan(dec) * Math.cos(phi));
  return { alt: (alt * 180) / Math.PI, az };
}
const wayTo = (alt, az) => { const a = (alt * Math.PI) / 180; return new THREE.Vector3(-Math.sin(az) * Math.cos(a), Math.sin(a), Math.cos(az) * Math.cos(a)); };

// Dusk and dawn for what is lit by hand: the lanterns at dusk, the windows a little later; after midnight the windows go out one by one.
const LAMPS_UP_DEG = [1.5, -3], WINDOWS_UP_DEG = [3, -4.5], BED = [0.5, 4, 0.6];

// Everything that follows the sun, by its altitude, from the night to the high day (Küstrin's table; the high day a touch bluer and clearer, the plain of Beijing on a clear day). Display colours for the sky, as they reach the screen: it is drawn without tone mapping, so the haze can meet it exactly. glowBand: the sunset's band along the horizon. haze: the haze's colour at middle distance, before it turns to the horizon's.
const SKY = [
  { alt: -11, zenith: [0.012, 0.022, 0.06], horizon: [0.05, 0.075, 0.14], glow: [0.05, 0.05, 0.10], cloudLit: [0.04, 0.05, 0.09], cloudDark: [0.015, 0.025, 0.055], haze: [0.035, 0.055, 0.11], sun: [1, 0.48, 0.24], sunI: 0, moonI: 0.3, hemiSky: [0.30, 0.38, 0.70], hemiGround: [0.12, 0.14, 0.22], hemiI: 0.24, exposure: 2.1, glowBand: 0.05 },
  { alt: -8, zenith: [0.022, 0.045, 0.125], horizon: [0.085, 0.12, 0.24], glow: [0.15, 0.13, 0.2], cloudLit: [0.07, 0.08, 0.16], cloudDark: [0.03, 0.04, 0.10], haze: [0.06, 0.09, 0.19], sun: [1, 0.48, 0.24], sunI: 0, moonI: 0.18, hemiSky: [0.30, 0.38, 0.70], hemiGround: [0.10, 0.12, 0.20], hemiI: 0.26, exposure: 1.9, glowBand: 0.1 },
  { alt: -5, zenith: [0.05, 0.105, 0.28], horizon: [0.20, 0.29, 0.52], glow: [0.5, 0.3, 0.3], cloudLit: [0.20, 0.23, 0.40], cloudDark: [0.08, 0.11, 0.24], haze: [0.15, 0.22, 0.42], sun: [1, 0.48, 0.24], sunI: 0, moonI: 0, hemiSky: [0.34, 0.42, 0.72], hemiGround: [0.16, 0.18, 0.26], hemiI: 0.36, exposure: 1.6, glowBand: 0.4 },
  { alt: -2.5, zenith: [0.11, 0.19, 0.42], horizon: [0.56, 0.45, 0.52], glow: [0.95, 0.40, 0.22], cloudLit: [0.56, 0.36, 0.42], cloudDark: [0.18, 0.19, 0.34], haze: [0.36, 0.33, 0.46], sun: [1, 0.48, 0.24], sunI: 0, moonI: 0, hemiSky: [0.42, 0.46, 0.70], hemiGround: [0.28, 0.27, 0.32], hemiI: 0.5, exposure: 1.35, glowBand: 0.8 },
  { alt: -0.8, zenith: [0.20, 0.27, 0.46], horizon: [0.94, 0.55, 0.37], glow: [1, 0.45, 0.22], cloudLit: [0.92, 0.50, 0.37], cloudDark: [0.36, 0.30, 0.40], haze: [0.55, 0.42, 0.44], sun: [1, 0.48, 0.24], sunI: 0, moonI: 0, hemiSky: [0.52, 0.49, 0.66], hemiGround: [0.38, 0.34, 0.35], hemiI: 0.58, exposure: 1.22, glowBand: 1 },
  { alt: 0.5, zenith: [0.22, 0.30, 0.50], horizon: [0.98, 0.58, 0.36], glow: [1, 0.48, 0.22], cloudLit: [0.98, 0.55, 0.38], cloudDark: [0.40, 0.33, 0.42], haze: [0.58, 0.45, 0.45], sun: [1, 0.48, 0.24], sunI: 1.1, moonI: 0, hemiSky: [0.55, 0.50, 0.65], hemiGround: [0.40, 0.35, 0.35], hemiI: 0.62, exposure: 1.18, glowBand: 1 },
  { alt: 5, zenith: [0.30, 0.40, 0.62], horizon: [0.98, 0.74, 0.50], glow: [1, 0.62, 0.30], cloudLit: [1, 0.78, 0.58], cloudDark: [0.60, 0.50, 0.56], haze: [0.62, 0.56, 0.58], sun: [1, 0.66, 0.38], sunI: 2.2, moonI: 0, hemiSky: [0.64, 0.62, 0.72], hemiGround: [0.52, 0.45, 0.40], hemiI: 0.85, exposure: 1.1, glowBand: 0.7 },
  { alt: 12, zenith: [0.33, 0.47, 0.70], horizon: [0.88, 0.83, 0.78], glow: [1, 0.75, 0.5], cloudLit: [1, 0.95, 0.88], cloudDark: [0.78, 0.76, 0.80], haze: [0.60, 0.64, 0.70], sun: [1, 0.82, 0.64], sunI: 2.3, moonI: 0, hemiSky: [0.67, 0.70, 0.82], hemiGround: [0.56, 0.51, 0.45], hemiI: 1.05, exposure: 1.05, glowBand: 0.15 },
  { alt: 38, zenith: [0.28, 0.48, 0.80], horizon: [0.74, 0.83, 0.92], glow: [1, 0.93, 0.80], cloudLit: [0.98, 0.98, 0.98], cloudDark: [0.86, 0.88, 0.92], haze: [0.55, 0.66, 0.80], sun: [1, 0.95, 0.87], sunI: 3, moonI: 0, hemiSky: [0.70, 0.80, 1], hemiGround: [0.58, 0.54, 0.47], hemiI: 1.3, exposure: 1.05, glowBand: 0 },
];
const MOON_COLOUR = [0.50, 0.62, 1];

function sunState(hour, season) {
  const S = SEASONS[season] || SEASONS.summer;
  const sunAt = skyPoint(hour, S.noon, S.declination), moonAt = skyPoint(hour < 12 ? hour + 24 : hour, S.noon + 12, -S.declination);
  let i = 0;
  while (i < SKY.length - 2 && sunAt.alt > SKY[i + 1].alt) i++;
  const a = SKY[i], b = SKY[i + 1], t = Math.min(Math.max((sunAt.alt - a.alt) / (b.alt - a.alt), 0), 1), out = {};
  for (const key of Object.keys(a)) out[key] = Array.isArray(a[key]) ? mix3(a[key], b[key], t) : a[key] + (b[key] - a[key]) * t;
  const sunUp = out.sunI > 0;
  // The light in the view: the sun while it gives any, then the moon. They never overlap, so it can change its direction unseen.
  out.dir = sunUp ? wayTo(Math.max(sunAt.alt, LOW_SUN_DEG), sunAt.az) : wayTo(Math.max(moonAt.alt, 8), moonAt.az);
  out.light = sunUp ? out.sun : MOON_COLOUR;
  out.lightI = sunUp ? out.sunI : out.moonI * smooth(-2, 12, moonAt.alt);
  out.sunDir = wayTo(sunAt.alt, sunAt.az); // where the sun really is, for the sky
  out.sunAlt = sunAt.alt;
  out.moonDir = wayTo(moonAt.alt, moonAt.az);
  out.moonShow = smooth(-1, -6, sunAt.alt) * smooth(-1, 2, moonAt.alt);
  out.stars = smooth(-5, -10.5, sunAt.alt);
  out.lampsOn = smooth(LAMPS_UP_DEG[0], LAMPS_UP_DEG[1], sunAt.alt);
  out.lit = smooth(WINDOWS_UP_DEG[0], WINDOWS_UP_DEG[1], sunAt.alt) * (hour < 12 ? 1 - BED[2] * smooth(BED[0], BED[1], hour) : 1);
  return out;
}
const toLinear = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const hexOf = (rgb) => `#${rgb.map((v) => Math.round(Math.min(Math.max(v, 0), 1) * 255).toString(16).padStart(2, "0")).join("")}`;

// The day of a season, for the header: sunrise and sunset by the clock, the slider's colours, what part of the day an hour is. 3d.js asks for it.
export function dayOf(season) {
  const S = SEASONS[season] || SEASONS.summer, alt = (h) => skyPoint(h, S.noon, S.declination).alt;
  const cross = (a, b) => { for (let k = 0; k < 40; k++) { const m = (a + b) / 2; if ((alt(m) > -0.83) === (alt(a) > -0.83)) a = m; else b = m; } return (a + b) / 2; };
  const rise = cross(0, S.noon), set = cross(S.noon, 24);
  const track = [];
  for (let h = 0; h <= 24; h += 0.5) { const s = sunState(h, season); track.push([h, hexOf(mix3(mix3(s.horizon, s.zenith, 0.45), s.glow, 0.35 * s.glowBand))]); }
  const partOf = (h) => {
    const a = alt(h);
    if (a < -6) return "night";
    if (a < 0) return h < S.noon ? "dawn" : "blue hour";
    if (a < 6) return h < S.noon ? "sunrise" : "sunset";
    if (a < 15) return h < S.noon ? "morning" : "golden hour";
    if (Math.abs(h - S.noon) < 1.5) return "noon";
    return h < S.noon ? "morning" : "afternoon";
  };
  // While the day plays, twice as slow through dawn and dusk
  return { rise, set, noon: S.noon, day: S.day, track, partOf, slow: [[rise - 0.8, rise + 1.2], [set - 1, set + 1.7]], down: (h) => alt(h) < -0.83 };
}

// ---- The patch every lit material takes ----
const PARS = `
uniform sampler2D uBeautyAO;
uniform vec4 uBeautyBox;
uniform vec4 uBeautyAOScale;
uniform vec3 uBeautySunDir;
uniform vec3 uBeautySunColour;
uniform vec3 uBeautyZenith;
uniform vec3 uBeautyHorizon;
uniform float uBeautyFarOn;
uniform sampler2D uBeautyLamps;
uniform vec4 uBeautyLampBox;
uniform float uBeautyLampsOn, uBeautyLit, uBeautyWindow, uBeautyVx, uBeautyMoon;
uniform vec3 uHazeFar, uHazeMid, uHazeGlow, uHazeSun;
uniform float uHazeK, uHazeH;
float beautySun = 1.0;
float beautyAO = 1.0;
vec3 beautyWorld;
#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS == 2
float beautyEdge( vec4 c ) { vec2 p = c.xy / c.w; return 2.0 * max( abs( p.x - 0.5 ), abs( p.y - 0.5 ) ); }
float beautyShadow() {
  float toFar = smoothstep( 0.84, 0.98, beautyEdge( vDirectionalShadowCoord[ 0 ] ) ), s = 1.0;
  if ( toFar < 1.0 ) s = getShadow( directionalShadowMap[ 0 ], directionalLightShadows[ 0 ].shadowMapSize, directionalLightShadows[ 0 ].shadowIntensity, directionalLightShadows[ 0 ].shadowBias, directionalLightShadows[ 0 ].shadowRadius, vDirectionalShadowCoord[ 0 ] );
  if ( toFar > 0.0 ) {
    float f = 1.0;
    if ( uBeautyFarOn > 0.5 ) f = mix( getShadow( directionalShadowMap[ 1 ], directionalLightShadows[ 1 ].shadowMapSize, directionalLightShadows[ 1 ].shadowIntensity, directionalLightShadows[ 1 ].shadowBias, directionalLightShadows[ 1 ].shadowRadius, vDirectionalShadowCoord[ 1 ] ), 1.0, smoothstep( 0.88, 1.0, beautyEdge( vDirectionalShadowCoord[ 1 ] ) ) );
    s = mix( s, f, toFar );
  }
  return s;
}
#endif
float beautyOcclusion( vec3 p ) {
  if ( uBeautyAOScale.w <= 0.0 ) return 1.0;
  vec2 uv = ( p.xz - uBeautyBox.xy ) * uBeautyBox.zw;
  if ( uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0 ) return 1.0;
  vec2 h = texture2D( uBeautyAO, uv ).rg * uBeautyAOScale.y + uBeautyAOScale.x;
  float close = clamp( ( h.x - p.y ) / ( 4.0 * uBeautyAOScale.z ), 0.0, 1.0 ), wide = clamp( ( h.y - p.y ) / ( 14.0 * uBeautyAOScale.z ), 0.0, 1.0 );
  return 1.0 - uBeautyAOScale.w * ( 0.45 * close + 0.55 * wide );
}
// The lanterns' map (night3d.js): at this point, moved along its normal so a wall takes what stands before it. Over the lantern's height it fades, or the roofs would light up.
vec3 beautyLamps( vec3 p, vec3 n ) {
  vec2 uv = ( p.xz + n.xz * 1.5 - uBeautyLampBox.xy ) * uBeautyLampBox.zw;
  if ( uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0 ) return vec3( 0.0 );
  vec4 t = texture2D( uBeautyLamps, uv );
  if ( t.r < 0.003 ) return vec3( 0.0 );
  float above = p.y / uBeautyVx - ( t.g / t.r * 60.0 - 10.0 );
  return ( 1.0 - exp( - 1.5 * t.r ) ) * ( 1.0 - smoothstep( 2.5, 7.0, above ) ) * vec3( 1.0, 0.44, 0.15 ); // about 2000 K through red paper; lanterns add up, but never to daylight
}
float beautyHash( vec2 p ) { return fract( sin( dot( p, vec2( 127.1, 311.7 ) ) ) * 43758.5453 ); }
float beautyNoise( vec2 p ) { vec2 i = floor( p ), f = fract( p ); f = f * f * ( 3.0 - 2.0 * f ); return mix( mix( beautyHash( i ), beautyHash( i + vec2( 1, 0 ) ), f.x ), mix( beautyHash( i + vec2( 0, 1 ) ), beautyHash( i + vec2( 1, 1 ) ), f.x ), f.y ); }
vec3 beautySky( vec3 r ) { return mix( uBeautyHorizon, uBeautyZenith, pow( clamp( r.y, 0.0, 1.0 ), 0.55 ) ); }
// A window: its id in 0-1 is the order in which it comes on; tone and strength from the same number. Paper on a lattice: warm and soft.
vec3 beautyWindowLight( float id ) {
  float tone = fract( id * 161.8 ), power = fract( id * 97.3 );
  float on = smoothstep( id - 0.03, id + 0.01, uBeautyLit );
  float far = 1.0 + 1.7 * smoothstep( 110.0, 800.0, distance( cameraPosition, beautyWorld ) ); // a window a pixel wide still catches the eye
  vec3 q = beautyWorld;
  float room = 0.76 + 0.24 * sin( q.x * 1.7 + q.z * 1.3 + 6.0 * tone ) * sin( q.y * 2.1 + 6.0 * power ); // no room is lit evenly: a lamp, a screen
  return on * far * room * uBeautyWindow * mix( 0.45, 1.15, power * power ) * mix( vec3( 1.0, 0.42, 0.11 ), vec3( 1.0, 0.58, 0.22 ), tone );
}
#if defined( TONE_MAPPING )
vec3 beautyGrade( vec3 c ) {
  float l = dot( c, vec3( 0.2126, 0.7152, 0.0722 ) );
  c = pow( max( c, vec3( 0.0 ) ) / 0.2, vec3( 1.2 ) ) * 0.2; // AgX is flat; a photo has more contrast than that
  l = dot( c, vec3( 0.2126, 0.7152, 0.0722 ) );
  c = mix( vec3( l ), c, 1.05 );
  return c * mix( vec3( 0.985, 0.995, 1.015 ), vec3( 1.012, 1.0, 0.982 ), smoothstep( 0.08, 0.6, l ) );
}
#endif
`;
const SHADOW_CALL = "directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;";
const LIGHTS = THREE.ShaderChunk.lights_fragment_begin.replace(SHADOW_CALL, `#if UNROLLED_LOOP_INDEX == 0
  if ( receiveShadow ) { beautySun = beautyShadow(); directLight.color *= beautySun; }
  #endif`);
const WORLD_POINT = "beautyWorld = transpose( mat3( viewMatrix ) ) * ( - vViewPosition ) + cameraPosition;";
const OCCLUDE = `
  beautyAO = beautyOcclusion( beautyWorld );
  reflectedLight.indirectDiffuse *= beautyAO;
  reflectedLight.directDiffuse *= mix( 1.0, beautyAO, 0.3 );
  // By moonlight the eye loses colour. Only the reflected light: the lanterns and the windows, added below, keep theirs.
  if ( uBeautyMoon > 0.001 ) {
    float seenD = dot( reflectedLight.directDiffuse, vec3( 0.2126, 0.7152, 0.0722 ) ), seenI = dot( reflectedLight.indirectDiffuse, vec3( 0.2126, 0.7152, 0.0722 ) );
    reflectedLight.directDiffuse = mix( reflectedLight.directDiffuse, seenD * vec3( 0.72, 0.84, 1.18 ), 0.5 * uBeautyMoon );
    reflectedLight.indirectDiffuse = mix( reflectedLight.indirectDiffuse, seenI * vec3( 0.72, 0.84, 1.18 ), 0.5 * uBeautyMoon );
  }
  if ( uBeautyLampsOn > 0.001 ) totalEmissiveRadiance += uBeautyLampsOn * ( 1.0 - 0.45 * smoothstep( 180.0, 900.0, distance( cameraPosition, beautyWorld ) ) ) * diffuseColor.rgb * beautyLamps( beautyWorld, transpose( mat3( viewMatrix ) ) * normal ); // from high up the pools would read as spots: the windows carry the far view`;
// A model's window, from the attribute (night3d.js gives each pane its lamp, 0 dark).
const WINDOW_LIGHT = `
  if ( vLamp > 0.002 && uBeautyLit > 0.001 ) totalEmissiveRadiance += beautyWindowLight( vLamp );`;
// A kit hall's window: the pane's own colour marks it; which are lit, by cells of the gardens (about a bay wide, a storey high), seeded.
const KIT_WINDOW = `
  #ifdef USE_COLOR
  if ( uBeautyLit > 0.001 && all( lessThan( abs( vColor.rgb * 255.0 - ${PANE} ), vec3( 0.6 ) ) ) ) {
    vec3 cell = floor( vec3( beautyWorld.x / 2.8, beautyWorld.y / ( 3.6 * uBeautyVx ), beautyWorld.z / 2.8 ) );
    float id = fract( sin( dot( cell, vec3( 12.9898, 78.233, 37.719 ) ) ) * 43758.5453 );
    if ( id < 0.5 ) totalEmissiveRadiance += 1.3 * beautyWindowLight( 0.004 + id * 1.9 );
  }
  #endif`;
// Water: the land's own vertex colour marks it where it is drawn with the land (the canals beyond the walls); the lakes have a material of their own. Ripples only tilt the reflection, and fade out before they would shimmer.
const WATER_BASE = (forced) => `
  float beautyWet = ${forced ? "1.0" : `clamp( 1.0 - distance( diffuseColor.rgb, ${WATER} ) / 0.06, 0.0, 1.0 )`};
  beautyWet = beautyWet * beautyWet * ( 3.0 - 2.0 * beautyWet );
  diffuseColor.rgb = mix( diffuseColor.rgb, vec3( 0.07, 0.12, 0.125 ), beautyWet );`;
// The land is one colour a kind over kilometres; in this light it takes a faint mottle of fields and fallow, a look, not a survey. Not on the water.
const MOTTLE = `
  {
    vec2 m = beautyWorld.xz / 210.0;
    float n = 0.65 * beautyNoise( m ) + 0.35 * beautyNoise( m * 3.7 + 5.3 );
    diffuseColor.rgb *= mix( vec3( 1.0 ), ( 0.9 + 0.2 * n ) * mix( vec3( 1.03, 0.99, 0.94 ), vec3( 0.96, 1.02, 0.98 ), n ), 1.0 - beautyWet );
  }`;
const WATER_TOP = `
  if ( beautyWet > 0.0 ) {
    vec3 toEye = cameraPosition - beautyWorld;
    float away = length( toEye );
    toEye /= away;
    vec2 q = beautyWorld.xz;
    q += 2.3 * sin( q.yx * vec2( 0.37, 0.29 ) ) + 0.9 * sin( q.yx * vec2( 0.91, 1.13 ) ); // warped, or the sines show as a weave
    vec2 g = vec2( cos( q.x * 0.71 + q.y * 0.33 ) + 0.6 * cos( q.x * 1.73 - q.y * 1.19 ) + 0.4 * cos( q.x * 3.1 + q.y * 2.3 ), cos( q.y * 0.83 - q.x * 0.27 ) + 0.6 * cos( q.y * 1.91 + q.x * 1.07 ) + 0.4 * cos( q.y * 3.7 - q.x * 1.9 ) );
    float tilt = mix( 0.035, 0.006, smoothstep( 25.0, 350.0, away ) );
    vec3 up = normalize( vec3( g.x * tilt, 1.0, g.y * tilt ) );
    vec3 r = reflect( - toEye, up );
    r.y = abs( r.y );
    q = beautyWorld.xz;
    float wind = 0.5 + 0.25 * sin( q.x * 0.013 + q.y * 0.021 + 2.0 * sin( q.y * 0.007 ) ) + 0.25 * sin( q.x * 0.041 - q.y * 0.017 + 1.5 * sin( q.x * 0.011 ) ); // long pale streaks: no water is one colour from above
    float fres = 0.2 + 0.1 * wind + 0.7 * pow( 1.0 - max( dot( up, toEye ), 0.0 ), 5.0 );
    float shine = pow( max( dot( r, uBeautySunDir ), 0.0 ), mix( 900.0, 140.0, smoothstep( 30.0, 1200.0, away ) ) );
    reflectedLight.directDiffuse *= 1.0 - beautyWet * fres;
    reflectedLight.indirectDiffuse *= 1.0 - beautyWet * fres;
    vec3 skyR = mix( uBeautyHorizon, uBeautyZenith, smoothstep( 0.03, 0.5, r.y ) ); // from above, water shows the sky over it; only a low eye sees the band along the horizon in it
    totalEmissiveRadiance += beautyWet * ( fres * mix( skyR, uBeautyHorizon, 0.12 ) + 1.6 * shine * beautySun * uBeautySunColour ); // rough water sees a wide patch of the sky, so a little paler
    // The lanterns on it, without a reflection: the mirror's own geometry, looking along the map. From an eye at height H, a light of height h shows on the water where it stands d h / H beyond it. Four heights, and the ripples smear it.
    if ( uBeautyLampsOn > 0.001 && away < 3000.0 ) {
      vec2 ahead = - toEye.xz / max( length( toEye.xz ), 0.001 );
      float reach = away / max( cameraPosition.y, 3.0 ), seen = 0.0;
      for ( int i = 0; i < 4; i ++ ) {
        float h = 1.5 + 1.5 * float( i );
        vec2 uv = ( beautyWorld.xz + ahead * ( reach * h + 2.0 * h * g.x ) - uBeautyLampBox.xy ) * uBeautyLampBox.zw;
        seen += textureLod( uBeautyLamps, uv, 1.0 ).r;
      }
      totalEmissiveRadiance += beautyWet * uBeautyLampsOn * ( 0.4 + 0.6 * wind ) * min( seen * 0.35, 0.6 ) * vec3( 1.0, 0.50, 0.20 );
    }
  }`;
// Glass takes the sky at a glance: panes are dark from the front and bright along the wall. The Xiyang Lou's glazed windows only; the Chinese halls' are paper.
const GLASS_TOP = `
  {
    vec3 toEye = normalize( cameraPosition - beautyWorld ), n = transpose( mat3( viewMatrix ) ) * normal;
    vec3 r = reflect( - toEye, n );
    r.y = abs( r.y );
    totalEmissiveRadiance += ( 0.05 + 0.75 * pow( 1.0 - max( dot( n, toEye ), 0.0 ), 3.0 ) ) * beautySky( r ) * mix( 0.35, 1.0, beautyAO );
  }`;
// The haze, in place of three's fog: after the tone mapping, in display colours, like the sky. Optical depth along the way from the eye, thinner with height; blue-grey at middle distance, the horizon's colour far off, warmer towards the sun.
const HAZE = `
#ifdef USE_FOG
  {
    vec3 toP = beautyWorld - cameraPosition;
    float dist = length( toP );
    float yMean = max( 0.5 * ( cameraPosition.y + beautyWorld.y ) / uBeautyVx, 0.0 );
    float tau = uHazeK * dist * exp( - yMean / uHazeH );
    float f = 1.0 - exp( - pow( tau, 1.3 ) );
    vec3 hz = mix( uHazeMid, uHazeFar, smoothstep( 0.35, 0.95, f ) );
    hz += uHazeGlow * pow( max( dot( toP / max( dist, 1.0 ), uHazeSun ), 0.0 ), 8.0 ) * 0.35;
    gl_FragColor.rgb = mix( gl_FragColor.rgb, hz, f );
  }
#endif`;

function patchShader(s, kind, shared) {
  Object.assign(s.uniforms, shared);
  const on = (anchor, text) => { s.fragmentShader = s.fragmentShader.replace(anchor, text); };
  const windows = kind === "glass" || kind === "lattice";
  if (windows) s.vertexShader = s.vertexShader.replace("#include <common>", "#include <common>\nattribute float aLamp;\nvarying float vLamp;").replace("#include <begin_vertex>", "#include <begin_vertex>\nvLamp = aLamp;");
  on("#include <shadowmap_pars_fragment>", `#include <shadowmap_pars_fragment>\n${windows ? "varying float vLamp;" : ""}\n${PARS}`);
  on("#include <lights_fragment_begin>", `${WORLD_POINT}\n${LIGHTS}`);
  const lighting = s.fragmentShader.includes("#include <lights_lambert_fragment>") ? "#include <lights_lambert_fragment>" : "#include <lights_phong_fragment>";
  const wet = kind === "ground" || kind === "water";
  if (wet) on(lighting, `${WATER_BASE(kind === "water")}\n${kind === "ground" ? MOTTLE : ""}\n${lighting}`);
  on("#include <aomap_fragment>", `#include <aomap_fragment>\n${OCCLUDE}\n${wet ? WATER_TOP : kind === "glass" ? GLASS_TOP : ""}\n${windows ? WINDOW_LIGHT : ""}${kind === "kit" ? KIT_WINDOW : ""}`);
  on("#include <tonemapping_fragment>", "#if defined( TONE_MAPPING )\n  gl_FragColor.rgb = beautyGrade( toneMapping( gl_FragColor.rgb ) );\n#endif");
  on("#include <fog_fragment>", HAZE);
}

const SKY_VERTEX = "varying vec3 vDir; void main() { vDir = position; vec4 p = projectionMatrix * modelViewMatrix * vec4( position, 1.0 ); gl_Position = p.xyww; }";
const SKY_FRAGMENT = `
varying vec3 vDir;
uniform vec3 uBeautyZenith, uBeautyHorizonShown, uBeautyGlow, uSkySun, uCloudLit, uCloudDark;
uniform vec3 uMoon;
uniform float uClouds, uGlowBand, uStars, uMoonShow;
float hash( vec2 p ) { return fract( sin( dot( p, vec2( 127.1, 311.7 ) ) ) * 43758.5453 ); }
float noise( vec2 p ) { vec2 i = floor( p ), f = fract( p ); f = f * f * ( 3.0 - 2.0 * f ); return mix( mix( hash( i ), hash( i + vec2( 1, 0 ) ), f.x ), mix( hash( i + vec2( 0, 1 ) ), hash( i + vec2( 1, 1 ) ), f.x ), f.y ); }
float fbm( vec2 p ) { float a = 0.5, v = 0.0; for ( int i = 0; i < 5; i ++ ) { v += a * noise( p ); p = p * 2.03 + 11.7; a *= 0.5; } return v; }
void main() {
  vec3 d = normalize( vDir );
  float up = max( d.y, 0.0 ), toSun = max( dot( d, uSkySun ), 0.0 );
  vec3 c = mix( uBeautyHorizonShown, uBeautyZenith, 1.0 - exp( - up * 3.6 ) );
  c += smoothstep( 0.0, 0.06, up ) * uBeautyGlow * ( 0.10 * pow( toSun, 6.0 ) + 0.22 * pow( toSun, 90.0 ) );
  // A low sun's band: along the horizon, on its side of the sky. It starts just above the land, where the haze has handed over.
  float round = 0.5 + 0.5 * dot( normalize( d.xz + vec2( 1e-5 ) ), normalize( uSkySun.xz + vec2( 1e-5 ) ) );
  c += uGlowBand * smoothstep( 0.0, 0.012, up ) * exp( - up * 7.0 ) * round * round * uBeautyGlow * 0.32;
  // The night: stars in cells of the sky, a little denser along a band, and a full moon with its dark seas.
  if ( uStars > 0.001 && up > 0.0 ) {
    vec2 sq = d.xz / ( 1.0 + d.y ) * 120.0, id = floor( sq );
    float a = hash( id ), b = hash( id + 7.3 ), band = exp( - pow( dot( d, vec3( 0.35, 0.28, - 0.894 ) ) * 3.5, 2.0 ) );
    float star = step( 0.925 - 0.05 * band, hash( id + 3.1 ) ) * smoothstep( 0.17, 0.02, length( fract( sq ) - 0.5 - ( vec2( a, b ) - 0.5 ) * 0.62 ) );
    c += smoothstep( 0.015, 0.2, up ) * uStars * ( star * ( 0.14 + 0.86 * a * a * b ) + 0.022 * band * fbm( d.xz * 9.0 + 4.0 ) * vec3( 0.8, 0.85, 1.0 ) );
  }
  if ( uMoonShow > 0.001 ) {
    float toMoon = dot( d, uMoon );
    c += uMoonShow * vec3( 0.55, 0.62, 0.78 ) * ( 0.05 * pow( max( toMoon, 0.0 ), 60.0 ) + 0.16 * pow( max( toMoon, 0.0 ), 900.0 ) );
    c = mix( c, vec3( 0.93, 0.93, 0.86 ) * ( 0.72 + 0.28 * smoothstep( 0.3, 0.62, fbm( d.xz * 150.0 ) ) ), uMoonShow * smoothstep( 0.99986, 0.99991, toMoon ) );
  }
  if ( uClouds > 0.5 && up > 0.015 ) {
    vec2 q = d.xz / ( up + 0.12 ) * 1.5;
    float n = fbm( q + vec2( 3.1, 7.7 ) );
    float cover = smoothstep( 0.56, 0.78, n ) * smoothstep( 0.015, 0.16, up ); // a few fair-weather clouds
    c = mix( c, mix( uCloudDark, uCloudLit, smoothstep( 0.45, 0.8, n + 0.15 * toSun + 0.1 * uGlowBand * round ) ), 0.78 * cover );
  }
  c += smoothstep( 0.9997, 0.99985, toSun ) * step( 0.0, d.y ) * step( 0.0, uSkySun.y + 0.005 ) * 0.8 * uBeautyGlow;
  gl_FragColor = vec4( c + ( hash( gl_FragCoord.xy ) - 0.5 ) / 255.0, 1.0 ); // a little dither: no bands in the gradient
}`;

const HEIGHT_VERTEX = `
varying float vH;
uniform float uY0, uRange;
void main() {
  vec4 p = vec4( position, 1.0 );
  #ifdef USE_INSTANCING
    p = instanceMatrix * p;
  #endif
  vec4 w = modelMatrix * p;
  vH = ( w.y - uY0 ) / uRange;
  gl_Position = projectionMatrix * viewMatrix * w;
}`;
const HEIGHT_FRAGMENT = "varying float vH; void main() { gl_FragColor = vec4( vH, 0.0, 0.0, 1.0 ); }";
const BLUR_FRAGMENT = `
varying vec2 vUv;
uniform sampler2D uSource;
uniform vec2 uStep;
uniform float uFirst;
void main() {
  // Two widths at once: red the close shade, green the wide one. The first pass reads both from red, the plain heights.
  float close = 0.0, wide = 0.0, cw = 0.0, ww = 0.0;
  for ( int i = - 12; i <= 12; i ++ ) {
    float x = float( i );
    vec4 t = texture2D( uSource, vUv + uStep * x );
    float a = exp( - x * x / ( 2.0 * 2.5 * 2.5 ) ), b = exp( - x * x / ( 2.0 * 6.5 * 6.5 ) );
    close += a * t.r; cw += a;
    wide += b * ( uFirst > 0.5 ? t.r : t.g ); ww += b;
  }
  gl_FragColor = vec4( close / cw, wide / ww, 0.0, 1.0 );
}`;

// meshes: { ground, around, aroundItems, structures, halls, ways (groups), greens, labels }; dynamic: groups whose meshes come and go (the kit's and the planting's near tiles), swept every frame for new ones. nightInputs: what night3d.js places its lanterns from.
export function createBeauty({ renderer, scene, camera, controls, world, hemi, sun, meshes, dynamic = [], state, render, draw, phone, automated, quality: asked, hour: askedHour, groundY = 1.5, nightInputs }) {
  let quality = asked && QUALITY[asked] ? asked : phone ? "low" : "high";
  const maxTexture = renderer.capabilities.maxTextureSize;
  const clean = { sunPos: sun.position.clone(), sunColour: sun.color.clone(), sunI: sun.intensity, hemiColour: hemi.color.clone(), hemiGround: hemi.groundColor.clone(), hemiI: hemi.intensity, fog: scene.fog, background: scene.background };
  const sunFar = new THREE.DirectionalLight(0xffffff, 0); // holds the second cascade; the light is all on `sun`
  const lights = [sun, sunFar];
  for (const l of lights) { scene.add(l.target); }
  const shared = {
    uBeautyAO: { value: null }, uBeautyBox: { value: new THREE.Vector4() }, uBeautyAOScale: { value: new THREE.Vector4() },
    uBeautySunDir: { value: new THREE.Vector3() }, uBeautySunColour: { value: new THREE.Color() }, uBeautyZenith: { value: new THREE.Color() }, uBeautyHorizon: { value: new THREE.Color() }, uBeautyFarOn: { value: 1 },
    uBeautyLamps: { value: null }, uBeautyLampBox: { value: new THREE.Vector4(0, 0, 1, 1) }, uBeautyLampsOn: { value: 0 }, uBeautyLit: { value: 0 }, uBeautyWindow: { value: 0 }, uBeautyVx: { value: 1 }, uBeautyMoon: { value: 0 },
    uHazeFar: { value: new THREE.Vector3() }, uHazeMid: { value: new THREE.Vector3() }, uHazeGlow: { value: new THREE.Vector3() }, uHazeSun: { value: new THREE.Vector3() }, uHazeK: { value: HAZE_PER_M }, uHazeH: { value: HAZE_HEIGHT_M },
  };
  const skyUniforms = { uBeautyZenith: { value: new THREE.Color() }, uBeautyHorizonShown: { value: new THREE.Color() }, uBeautyGlow: { value: new THREE.Color() }, uSkySun: { value: new THREE.Vector3() }, uCloudLit: { value: new THREE.Color() }, uCloudDark: { value: new THREE.Color() }, uClouds: { value: 1 }, uGlowBand: { value: 0 }, uMoon: { value: new THREE.Vector3() }, uStars: { value: 0 }, uMoonShow: { value: 0 } };
  const sky = new THREE.Mesh(new THREE.SphereGeometry(100000, 32, 16), new THREE.ShaderMaterial({ vertexShader: SKY_VERTEX, fragmentShader: SKY_FRAGMENT, uniforms: skyUniforms, side: THREE.BackSide, depthTest: false, depthWrite: false, toneMapped: false, fog: false }));
  sky.renderOrder = -1000;
  sky.frustumCulled = false;
  sky.raycast = () => {};
  const fog = new THREE.FogExp2(0xffffff, 0.00006); // the materials this mode doesn't patch (sprites, lines, unlit model parts) keep three's own fog with this; the rest take HAZE
  let enabled = false, hour = askedHour ?? SUN_DEFAULT_HOUR, season = state.season, sunNow = sunState(hour, season), baking = false, aoTimer = 0, shadowsDirty = true, stateSeen = "", cycling = false, stepNear = false, stepFar = false;
  const litDir = new THREE.Vector3(), farDir = new THREE.Vector3(); // where the light stands for the shadows and for the shading, so the two always agree; the far map's own

  // ---- The materials ----
  const saved = new Map();
  const dress = (m, kind) => {
    if (!m || saved.has(m) || !(m.isMeshLambertMaterial || m.isMeshPhongMaterial)) return;
    const before = m.onBeforeCompile, ownKey = Object.prototype.hasOwnProperty.call(m, "customProgramCacheKey") ? m.customProgramCacheKey : null, baseKey = m.customProgramCacheKey();
    saved.set(m, { before, ownKey });
    m.onBeforeCompile = function (s, r) { before.call(this, s, r); patchShader(s, kind, shared); };
    m.customProgramCacheKey = () => `${baseKey}|beauty|${kind}`;
    m.needsUpdate = true;
  };
  const undress = () => {
    for (const [m, s] of saved) {
      m.onBeforeCompile = s.before;
      if (s.ownKey) m.customProgramCacheKey = s.ownKey; else delete m.customProgramCacheKey;
      m.needsUpdate = true;
    }
    saved.clear();
  };

  // Who casts and who receives. What lies flat on the ground (a polygon offset: paths, courts, patches, lotus) or lets light through (water, panes) takes shadow but casts none.
  // A mesh with no normals (the halls' merged buffers) casts through a depth material with a slope-scaled offset, its stand-in for the normal bias; so does a double-sided one (the detailed models, the walls), whose lit face is in the map too.
  const slopeDepth = new THREE.MeshDepthMaterial({ polygonOffset: true, polygonOffsetFactor: 2.2, polygonOffsetUnits: 3 });
  const flagged = new Set();
  const flag = (o, cast, receive) => {
    o.castShadow = cast;
    o.receiveShadow = receive;
    if (cast && (!o.geometry.getAttribute("normal") || o.material.side === THREE.DoubleSide) && !o.customDepthMaterial) { o.customDepthMaterial = slopeDepth; o.userData.beautyDepth = true; }
    flagged.add(o);
  };
  const kindOf = (m, fallback) => (/^glass_win/.test(m.name || "") ? "glass" : /^glass_/.test(m.name || "") ? "lattice" : /^water/.test(m.name || "") ? "water" : fallback);
  const lays = (m) => m.transparent || m.polygonOffset;
  const dressTree = (root, kind, { cast = true } = {}) => {
    if (!root) return 0;
    let n = 0;
    root.traverse((o) => {
      if (!o.isMesh || flagged.has(o)) return;
      const m = o.material;
      if (!m || Array.isArray(m)) return;
      flag(o, cast && !lays(m) && !o.userData.noShadow, true);
      dress(m, typeof kind === "function" ? kind(o, m) : kindOf(m, kind));
      n++;
    });
    return n;
  };
  const prepare = () => {
    const M = meshes;
    dressTree(M.ground, (o, m) => (m.transparent ? "water" : "ground"));
    dressTree(M.around, (o, m) => (m.transparent ? "water" : "ground"));
    dressTree(M.aroundItems, "ground");
    dressTree(M.structures, "plain");
    dressTree(M.halls, (o, m) => (m === HallBuffer.material ? "kit" : kindOf(m, "plain")));
    for (const g of Object.values(M.ways || {})) dressTree(g, "plain");
    dressTree(M.greens, "plain");
    if (night) { night.lightModels(); dressTree(night.group, "plain", { cast: false }); }
  };
  // New near tiles of the kit and the planting: flagged and dressed as they come; the near map is drawn again.
  const sweep = () => {
    let n = 0;
    for (const g of dynamic) n += dressTree(g, (o, m) => (m === HallBuffer.material ? "kit" : kindOf(m, "plain")));
    if (n) { sun.shadow.needsUpdate = true; if (night) night.lightModels(); }
    // drop the ones gone, so the set stays small
    if (flagged.size > 4000) for (const o of flagged) if (!o.parent) flagged.delete(o);
  };
  const unflag = () => {
    for (const o of flagged) { o.castShadow = o.receiveShadow = false; if (o.userData.beautyDepth) { o.customDepthMaterial = undefined; delete o.userData.beautyDepth; } }
    flagged.clear();
  };

  // ---- The sun ----
  const applySun = (gently = false) => {
    sunNow = sunState(hour, season);
    const s = sunNow;
    sun.color.setRGB(...s.light);
    sun.intensity = s.lightI;
    hemi.color.setRGB(...s.hemiSky);
    hemi.groundColor.setRGB(...s.hemiGround);
    hemi.intensity = s.hemiI;
    renderer.toneMappingExposure = s.exposure;
    shared.uBeautySunDir.value.copy(s.dir);
    shared.uBeautySunColour.value.setRGB(...s.light).multiplyScalar(s.lightI);
    shared.uBeautyZenith.value.setRGB(...s.zenith.map(toLinear));
    shared.uBeautyHorizon.value.setRGB(...s.horizon.map(toLinear));
    skyUniforms.uBeautyZenith.value.setRGB(...s.zenith);
    skyUniforms.uBeautyHorizonShown.value.setRGB(...s.horizon);
    skyUniforms.uBeautyGlow.value.setRGB(...s.glow);
    skyUniforms.uSkySun.value.copy(s.sunDir);
    skyUniforms.uCloudLit.value.setRGB(...s.cloudLit);
    skyUniforms.uCloudDark.value.setRGB(...s.cloudDark);
    skyUniforms.uGlowBand.value = s.glowBand;
    skyUniforms.uMoon.value.copy(s.moonDir);
    skyUniforms.uMoonShow.value = s.moonShow;
    skyUniforms.uStars.value = s.stars;
    shared.uHazeFar.value.set(...s.horizon);
    shared.uHazeMid.value.set(...s.haze);
    shared.uHazeGlow.value.set(...s.glow).multiplyScalar(Math.max(s.glowBand, 0.15) * smooth(-8, 2, s.sunAlt));
    shared.uHazeSun.value.copy(s.sunDir);
    const assumedOn = state.assumed !== false;
    const lampsOn = night && assumedOn ? s.lampsOn : 0, lit = night && assumedOn ? s.lit : 0;
    shared.uBeautyLampsOn.value = lampsOn * 0.5;
    shared.uBeautyLit.value = lit;
    shared.uBeautyWindow.value = 0.34;
    shared.uBeautyMoon.value = s.moonShow;
    night?.setLight(lampsOn, lit);
    fog.color.setRGB(...s.horizon, THREE.SRGBColorSpace);
    if (!gently) {
      litDir.copy(s.dir);
      farDir.copy(s.dir);
      shadowsDirty = true;
    } else if (s.lightI > 0 && (s.dir.angleTo(litDir) * 180) / Math.PI >= Math.min(Math.max((cascades[0].half / STEP_NEAR_AT_M) * STEP_NEAR_DEG[1], STEP_NEAR_DEG[0]), STEP_NEAR_DEG[1])) { // between the sun and the moon there is no light, and nothing to redraw
      litDir.copy(s.dir);
      stepNear = true;
      if ((s.dir.angleTo(farDir) * 180) / Math.PI >= STEP_FAR_DEG) { farDir.copy(s.dir); stepFar = true; }
    }
  };

  // ---- The cascades ----
  const cascades = lights.map(() => ({ cu: 0, cv: 0, half: 0, range: 0 }));
  const U = new THREE.Vector3(), V = new THREE.Vector3(), L = new THREE.Vector3(), p = new THREE.Vector3(), ray = new THREE.Vector3(), UP = new THREE.Vector3(0, 1, 0), centre = new THREE.Vector3();
  const CORNERS = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
  // The square, in the light's own plane, holding what the camera sees of the ground out to `reach` metres.
  const wanted = (reach) => {
    let u0 = Infinity, u1 = -Infinity, v0 = Infinity, v1 = -Infinity;
    const add = (q) => {
      const a = q.dot(U), b = q.dot(V);
      u0 = Math.min(u0, a); u1 = Math.max(u1, a); v0 = Math.min(v0, b); v1 = Math.max(v1, b);
    };
    add(camera.position);
    const C = camera.position, ground = groundY * world.scale.y;
    for (const [x, y] of CORNERS) {
      ray.set(x, y, 0.5).unproject(camera).sub(C).normalize();
      const hit = ray.y < -1e-3 ? (ground - C.y) / ray.y : Infinity;
      add(p.copy(C).addScaledVector(ray, Math.min(hit, reach)));
    }
    return { cu: (u0 + u1) / 2, cv: (v0 + v1) / 2, half: Math.max(u1 - u0, v1 - v0) / 2 };
  };
  const fitCascade = (i, want, size, force) => {
    const c = cascades[i], light = lights[i];
    const inside = c.half && Math.abs(want.cu - c.cu) + want.half <= c.half && Math.abs(want.cv - c.cv) + want.half <= c.half && want.half >= c.half * 0.55;
    if (inside && !force) return false;
    const half = Math.max(want.half * 1.22, 24), texel = (2 * half) / size;
    c.half = half;
    // On the texel grid, so the edges don't crawl when the fit moves.
    c.cu = Math.round(want.cu / texel) * texel;
    c.cv = Math.round(want.cv / texel) * texel;
    const sinAlt = Math.max(L.y, 0.05), cosAlt = Math.sqrt(1 - L.y ** 2), spread = half * Math.SQRT2 * cosAlt;
    const back = spread + (CASTERS_TOP_M[i] * world.scale.y) / sinAlt + 60;
    centre.set(0, 0, 0).addScaledVector(U, c.cu).addScaledVector(V, c.cv);
    // Along the sun's line: where this column meets the ground.
    centre.addScaledVector(L, (groundY * world.scale.y - centre.y) / L.y);
    light.position.copy(centre).addScaledVector(L, back);
    light.target.position.copy(centre);
    light.updateMatrixWorld();
    light.target.updateMatrixWorld();
    const cam = light.shadow.camera;
    cam.left = cam.bottom = -half;
    cam.right = cam.top = half;
    cam.near = 1;
    cam.far = back + spread + 80;
    cam.updateProjectionMatrix();
    c.range = cam.far - cam.near;
    light.shadow.radius = i === 0 ? 1.7 : 1.3;
    light.shadow.normalBias = Math.min(texel * 1.6, 3);
    light.shadow.bias = -(texel * 1.3) / c.range;
    light.shadow.needsUpdate = true;
    return true;
  };
  const fullRatio = Math.min(devicePixelRatio, 2);
  const setRatio = () => { const r = enabled && quality === "low" ? Math.min(fullRatio, 1.5) : enabled && QUALITY[quality].ratio ? Math.min(fullRatio, QUALITY[quality].ratio) : fullRatio; if (renderer.getPixelRatio() !== r) renderer.setPixelRatio(r); };
  const sizes = () => { const q = QUALITY[quality]; return [Math.min(q.near, maxTexture), Math.min(q.far || 16, maxTexture)]; }; // one cascade: the second map stays, tiny and never read, so no material has to change
  const setSizes = () => {
    const s = sizes();
    lights.forEach((l, i) => {
      if (l.shadow.mapSize.x === s[i] && l.shadow.map) return;
      l.shadow.mapSize.set(s[i], s[i]);
      if (l.shadow.map) { l.shadow.map.dispose(); l.shadow.map = null; }
    });
    shadowsDirty = true;
  };
  const updateCascades = () => {
    L.copy(litDir);
    U.crossVectors(UP, L).normalize();
    V.crossVectors(L, U);
    const one = !QUALITY[quality].far, d = camera.position.distanceTo(controls.target), reach = Math.max(d * (one ? 3.2 : 2.1), 130), s = sizes(), force = shadowsDirty, near = force || stepNear, farToo = force || stepFar;
    shadowsDirty = stepNear = stepFar = false;
    shared.uBeautyFarOn.value = one ? 0 : 1;
    let moved = fitCascade(0, wanted(reach), s[0], near);
    if (!one || force) moved = fitCascade(1, wanted(Math.min(Math.max(reach * 7, 2800), 40000)), s[1], farToo) || moved;
    return moved;
  };

  const onFrame = () => {
    if (baking) return;
    sky.position.copy(camera.position);
    sky.updateMatrixWorld();
    shared.uBeautyVx.value = world.scale.y;
    sweep();
    night?.onFrame();
    updateCascades();
  };

  // ---- The occlusion: heights from straight above, blurred at two widths, on one texture. Once, and again when what stands in the gardens changes.
  let aoHeights = null, aoPass = [], aoCamera = null, aoHeightMat = null, aoScene = null, aoQuad = null, blurMat = null;
  const makeTargets = () => {
    const q = QUALITY[quality], gl = renderer.getContext();
    disposeTargets();
    if (!q.ao) return;
    const float = gl.getExtension("EXT_color_buffer_float") || gl.getExtension("EXT_color_buffer_half_float");
    const opts = { type: float ? THREE.HalfFloatType : THREE.UnsignedByteType, format: THREE.RGBAFormat, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, generateMipmaps: false, depthBuffer: false };
    aoHeights = new THREE.WebGLRenderTarget(q.aoSource, q.aoSource, { ...opts, depthBuffer: true });
    aoPass = [new THREE.WebGLRenderTarget(q.ao, q.ao, opts), new THREE.WebGLRenderTarget(q.ao, q.ao, opts)];
    shared.uBeautyAO.value = aoPass[1].texture;
  };
  const disposeTargets = () => { if (aoHeights) aoHeights.dispose(); for (const t of aoPass) t.dispose(); aoHeights = null; aoPass = []; shared.uBeautyAO.value = null; };
  const bake = () => {
    if (!enabled) return;
    if (!QUALITY[quality].ao) { shared.uBeautyAOScale.value.set(0, 1, 1, 0); return; }
    if (!aoCamera) {
      const [x0, z0, x1, z1] = AO_BOX;
      aoCamera = new THREE.OrthographicCamera(-(x1 - x0) / 2, (x1 - x0) / 2, (z1 - z0) / 2, -(z1 - z0) / 2, 1, 2000);
      aoCamera.up.set(0, 0, -1);
      aoCamera.position.set((x0 + x1) / 2, 1000, (z0 + z1) / 2);
      aoCamera.lookAt((x0 + x1) / 2, 0, (z0 + z1) / 2);
      aoCamera.updateMatrixWorld();
      aoHeightMat = new THREE.ShaderMaterial({ vertexShader: HEIGHT_VERTEX, fragmentShader: HEIGHT_FRAGMENT, uniforms: { uY0: { value: 0 }, uRange: { value: 1 } }, side: THREE.DoubleSide, fog: false, toneMapped: false });
      blurMat = new THREE.ShaderMaterial({ vertexShader: "varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4( position.xy, 0.0, 1.0 ); }", fragmentShader: BLUR_FRAGMENT, uniforms: { uSource: { value: null }, uStep: { value: new THREE.Vector2() }, uFirst: { value: 1 } }, depthTest: false, depthWrite: false, fog: false, toneMapped: false });
      aoScene = new THREE.Scene();
      aoQuad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), blurMat);
      aoQuad.frustumCulled = false;
      aoScene.add(aoQuad);
    }
    if (!aoHeights) makeTargets();
    const [x0, z0, x1, z1] = AO_BOX, vx = world.scale.y, q = QUALITY[quality];
    baking = true;
    // Only what stands: the names, the night's lanterns and the sky are not in the height map.
    const hide = [sky, night?.group, ...(meshes.labels?.() || [])].filter(Boolean), was = hide.map((o) => o.visible);
    for (const o of hide) o.visible = false;
    const before = { target: renderer.getRenderTarget(), background: scene.background, fog: scene.fog, override: scene.overrideMaterial, tone: renderer.toneMapping, auto: renderer.shadowMap.autoUpdate, clear: renderer.getClearColor(new THREE.Color()), alpha: renderer.getClearAlpha() };
    renderer.shadowMap.autoUpdate = false;
    renderer.toneMapping = THREE.NoToneMapping;
    scene.background = null;
    scene.fog = null;
    scene.overrideMaterial = aoHeightMat;
    aoHeightMat.uniforms.uY0.value = AO_Y0 * vx;
    aoHeightMat.uniforms.uRange.value = AO_RANGE * vx;
    renderer.setClearColor(0x000000, 1);
    renderer.setRenderTarget(aoHeights);
    renderer.clear();
    renderer.render(scene, aoCamera);
    scene.overrideMaterial = before.override;
    blurMat.uniforms.uSource.value = aoHeights.texture;
    blurMat.uniforms.uStep.value.set(1 / q.ao, 0);
    blurMat.uniforms.uFirst.value = 1;
    renderer.setRenderTarget(aoPass[0]);
    renderer.render(aoScene, aoCamera);
    blurMat.uniforms.uSource.value = aoPass[0].texture;
    blurMat.uniforms.uStep.value.set(0, 1 / q.ao);
    blurMat.uniforms.uFirst.value = 0;
    renderer.setRenderTarget(aoPass[1]);
    renderer.render(aoScene, aoCamera);
    renderer.setRenderTarget(before.target);
    renderer.setClearColor(before.clear, before.alpha);
    renderer.toneMapping = before.tone;
    renderer.shadowMap.autoUpdate = before.auto;
    scene.background = before.background;
    scene.fog = before.fog;
    hide.forEach((o, i) => { o.visible = was[i]; });
    shared.uBeautyBox.value.set(x0, z1, 1 / (x1 - x0), -1 / (z1 - z0));
    shared.uBeautyAOScale.value.set(AO_Y0 * vx, AO_RANGE * vx, vx, AO_STRENGTH);
    baking = false;
  };
  const bakeSoon = () => { clearTimeout(aoTimer); aoTimer = setTimeout(() => { aoTimer = 0; if (enabled) { bake(); render(); } }, 500); };

  // ---- The night: its own module, fetched behind the first sun frame, so the day doesn't wait for it. A link to the night waits, through nightReady.
  let night = null, nightLoading = null;
  const loadNight = () => (nightLoading ||= (async () => {
    const res = await fetch("night3d.js");
    if (!res.ok) throw new Error(`night3d.js: ${res.status}`);
    const url = URL.createObjectURL(new Blob([await res.text(), "\n//# sourceURL=night3d.js"], { type: "text/javascript" }));
    let mod;
    try { mod = await import(url); } finally { URL.revokeObjectURL(url); }
    night = await mod.createNight({ renderer, world, camera, shared, box: AO_BOX, phone, state, models: meshes.halls, ...nightInputs });
    night.sync();
    if (enabled) { prepare(); applySun(); render(); } else night.setVisible(false);
  })().catch((err) => { console.warn("The night's lanterns are not loaded:", err); }));

  const enable = () => {
    if (enabled) return;
    enabled = true;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.shadowMap.autoUpdate = true;
    renderer.toneMapping = THREE.AgXToneMapping;
    scene.fog = fog;
    scene.add(sky, sunFar);
    for (const l of lights) { l.castShadow = true; l.shadow.autoUpdate = false; }
    skyUniforms.uClouds.value = QUALITY[quality].clouds ? 1 : 0;
    setRatio();
    season = state.season;
    prepare();
    applySun();
    setSizes();
    scene.onBeforeRender = onFrame;
    stateSeen = JSON.stringify(state);
    bake();
    shared.uBeautyVx.value = world.scale.y;
    night?.setVisible(true);
    loadNight();
  };
  const disable = () => {
    if (!enabled) return;
    enabled = false;
    clearTimeout(aoTimer);
    scene.onBeforeRender = () => {};
    night?.setVisible(false);
    for (const l of lights) {
      l.castShadow = false;
      if (l.shadow.map) { l.shadow.map.dispose(); l.shadow.map = null; }
    }
    for (const c of cascades) c.half = 0;
    scene.remove(sky, sunFar);
    scene.fog = clean.fog;
    scene.background = clean.background;
    renderer.toneMapping = THREE.NoToneMapping;
    renderer.toneMappingExposure = 1;
    renderer.shadowMap.enabled = false;
    setRatio();
    sun.position.copy(clean.sunPos);
    sun.target.position.set(0, 0, 0);
    sun.updateMatrixWorld();
    sun.target.updateMatrixWorld();
    sun.color.copy(clean.sunColour);
    sun.intensity = clean.sunI;
    hemi.color.copy(clean.hemiColour);
    hemi.groundColor.copy(clean.hemiGround);
    hemi.intensity = clean.hemiI;
    unflag();
    undress();
    disposeTargets();
  };

  // The probe: a frame's whole cost, to the last pixel. A real GPU that can't keep up steps down a quality; a phone starts low. Screenshot tools and a link's lightq= keep what they asked for.
  const px = new Uint8Array(4);
  const measure = () => {
    const gl = renderer.getContext(), t0 = performance.now();
    draw();
    gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
    return performance.now() - t0;
  };
  const applyQuality = (q) => {
    quality = q;
    setRatio();
    setSizes();
    skyUniforms.uClouds.value = QUALITY[q].clouds ? 1 : 0;
    disposeTargets();
    bake();
  };
  const probe = (force = false) => {
    if (!force && (automated || asked)) return;
    if (!enabled || quality === "min") return;
    measure(); // the first frame also compiles
    for (let tries = 0; tries < 3 && quality !== "min"; tries++) {
      if (Math.min(measure(), measure()) <= (quality === "low" ? STEP_TO_MIN_MS : STEP_DOWN_MS)) return;
      applyQuality(NEXT_DOWN[quality]);
      measure();
    }
  };

  return {
    enable, disable, probe, measure, bake,
    get on() { return enabled; },
    get quality() { return quality; },
    get hour() { return hour; },
    get season() { return season; },
    setHour(h) { hour = Math.min(Math.max(h, SUN_HOURS[0]), SUN_HOURS[1]); if (enabled) { applySun(); render(); } },
    // A step of the playing day: everything but the shadows moves, and no frame is drawn: 3d.js asks for those.
    stepHour(h) { hour = Math.min(Math.max(h, SUN_HOURS[0]), SUN_HOURS[1]); if (enabled) applySun(true); },
    // When the day stops, the light takes its exact place.
    set cycling(on) { const was = cycling; cycling = on; if (was && !on && enabled) applySun(); },
    get sunBelow() { return sunNow.sunAlt < 0; },
    state: () => ({ ...sunNow, dir: sunNow.dir.toArray(), sunDir: sunNow.sunDir.toArray(), moonDir: sunNow.moonDir.toArray() }),
    nightReady: () => loadNight(),
    get night() { return night; },
    setQuality(q) { if (!QUALITY[q]) return; if (enabled) { applyQuality(q); render(); } else quality = q; },
    // New models: their shadows and their patches, and the height map again, once they stop coming.
    modelsChanged() { if (enabled) { prepare(); shadowsDirty = true; bakeSoon(); } },
    moved() { sun.shadow.needsUpdate = true; },
    // A toggle, the season or the 2x option: what stands in the gardens, or the sun's path, may have changed.
    changed() {
      const now = JSON.stringify(state);
      if (!enabled || now === stateSeen) return;
      stateSeen = now;
      season = state.season;
      shadowsDirty = true;
      night?.sync();
      shared.uBeautyVx.value = world.scale.y;
      applySun();
      bakeSoon();
    },
    // How many materials wear the patch now (0 when Clean): tools/light_test.mjs reads it.
    get patched() { return saved.size; },
    stats: () => ({ night: night?.stats(), quality, patched: saved.size, flagged: flagged.size, cascades: cascades.map((c, i) => ({ half: Math.round(c.half), metresPerTexel: +((2 * c.half) / sizes()[i]).toFixed(3) })), programs: renderer.info.programs.length, tris: renderer.info.render.triangles, calls: renderer.info.render.calls }),
  };
}
