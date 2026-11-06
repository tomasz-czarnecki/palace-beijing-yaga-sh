// A small GLB reader for the site's three.js bundle, which has no GLTFLoader. Classic script: defines the global loadGLBLite(url), a promise of a THREE.Group.
// Round 13: copied from the sister project kostrzyn-yaga-sh (site/reconstruction/glb_lite.js); here it also honours a material's doubleSided, which scripts/model_mesh.py sets on every material.
// Reads what build_model.py writes: one node, one mesh, indexed primitives, a base colour and at most one embedded JPEG. Not a general glTF loader.
// Also what scripts/fortress_mesh.py writes: quantised positions with a node scale and translation (KHR_mesh_quantization), int8 normals, uint8 vertex colours.
async function loadGLBLite(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  const buf = await res.arrayBuffer(), view = new DataView(buf);
  if (view.getUint32(0, true) !== 0x46546c67) throw new Error(`${url}: not a GLB`);
  const jsonLen = view.getUint32(12, true);
  const gltf = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 20, jsonLen)));
  const binStart = 20 + jsonLen + 8;
  const TYPES = { 5126: Float32Array, 5125: Uint32Array, 5123: Uint16Array, 5122: Int16Array, 5121: Uint8Array, 5120: Int8Array };
  const arrayOf = (i) => {
    const a = gltf.accessors[i], v = gltf.bufferViews[a.bufferView], Type = TYPES[a.componentType];
    const size = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 }[a.type], start = binStart + (v.byteOffset || 0);
    if (!v.byteStride || v.byteStride === size * Type.BYTES_PER_ELEMENT) return new Type(buf.slice(start, start + a.count * size * Type.BYTES_PER_ELEMENT));
    const out = new Type(a.count * size), each = v.byteStride / Type.BYTES_PER_ELEMENT, all = new Type(buf.slice(start, start + a.count * v.byteStride));
    for (let k = 0; k < a.count; k++) for (let c = 0; c < size; c++) out[k * size + c] = all[k * each + c];
    return out;
  };
  // A quantised attribute as plain floats: the node's scale and translation for positions, the normalised range for the others.
  const floats = (i, scale, shift) => {
    const a = gltf.accessors[i], raw = arrayOf(i);
    if (a.componentType === 5126) return raw;
    const out = new Float32Array(raw.length), size = { VEC2: 2, VEC3: 3, VEC4: 4 }[a.type];
    const unit = a.normalized ? 1 / { 5123: 65535, 5122: 32767, 5121: 255, 5120: 127 }[a.componentType] : 1;
    for (let k = 0; k < raw.length; k++) out[k] = raw[k] * unit * (scale ? scale[k % size] : 1) + (shift ? shift[k % size] : 0);
    return out;
  };
  const node = gltf.nodes[0];
  let texture = null;
  if (gltf.images) {
    const v = gltf.bufferViews[gltf.images[0].bufferView];
    const blob = new Blob([new Uint8Array(buf, binStart + v.byteOffset, v.byteLength)], { type: gltf.images[0].mimeType });
    const bitmap = await createImageBitmap(blob, { imageOrientation: "flipY" });
    texture = new THREE.Texture(bitmap);
    texture.flipY = false;
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 8;
    texture.needsUpdate = true;
  }
  const group = new THREE.Group();
  group.name = gltf.nodes[0].name;
  group.userData = gltf.nodes[0].extras || {};
  for (const prim of gltf.meshes[0].primitives) {
    const def = gltf.materials[prim.material], pbr = def.pbrMetallicRoughness, geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(floats(prim.attributes.POSITION, node.scale, node.translation), 3));
    geo.setAttribute("normal", new THREE.BufferAttribute(floats(prim.attributes.NORMAL), 3));
    if (prim.attributes.COLOR_0 !== undefined) {
      const rgba = floats(prim.attributes.COLOR_0), rgb = new Float32Array((rgba.length / 4) * 3);
      for (let k = 0; k < rgba.length / 4; k++) rgb.set(rgba.subarray(k * 4, k * 4 + 3), k * 3);
      geo.setAttribute("color", new THREE.BufferAttribute(rgb, 3));
    }
    if (prim.attributes.TEXCOORD_0 !== undefined) {
      const uv = arrayOf(prim.attributes.TEXCOORD_0);
      // the texture was flipped when decoded, so uv's v runs the other way
      for (let i = 1; i < uv.length; i += 2) uv[i] = 1 - uv[i];
      geo.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
    }
    geo.setIndex(new THREE.BufferAttribute(arrayOf(prim.indices), 1));
    const opts = { name: def.name, side: def.doubleSided ? THREE.DoubleSide : THREE.FrontSide, vertexColors: prim.attributes.COLOR_0 !== undefined };
    if (pbr.baseColorTexture && texture) opts.map = texture;
    else opts.color = new THREE.Color().setRGB(...pbr.baseColorFactor.slice(0, 3));
    const unlit = def.extensions && def.extensions.KHR_materials_unlit;
    // glass_*: panes with a modest highlight (the arsenal, models/B05-zeughaus/arsenal.py). Plain "glass", which about 100 other models use, stays as it was.
    const lit = def.name.startsWith("glass_") ? new THREE.MeshPhongMaterial({ ...opts, specular: 0x3c4650, shininess: 60 }) : new THREE.MeshLambertMaterial(opts);
    group.add(new THREE.Mesh(geo, unlit ? new THREE.MeshBasicMaterial(opts) : lit));
  }
  return group;
}
