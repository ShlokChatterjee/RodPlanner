import * as THREE from 'three';
import { planToWorld } from './coords.js';

/**
 * Build an extruded mesh from a polygon footprint.
 *
 * @param {number[][]} polygon  Array of [x, y] pairs in metres (plan coordinates)
 * @param {number}     height   Building height in metres
 * @returns {THREE.Mesh}
 */
export function buildBuilding(polygon, height) {
  // ExtrudeGeometry draws a 2D shape in its own XY plane and extrudes along +Z.
  // We then rotate the mesh by -90° about X so it stands on the ground:
  //   shape (sx, sy, sz)  →  world (sx, sz, -sy)
  // So a shape point (sx, sy) lands at world x = sx, world z = -sy.
  // To land on planToWorld's z, we need sy = -world.z.
  const toShape = ([x, y]) => {
    const w = planToWorld(x, y);
    return [w.x, -w.z];
  };

  const shape = new THREE.Shape();
  const [x0, y0] = toShape(polygon[0]);
  shape.moveTo(x0, y0);
  for (let i = 1; i < polygon.length; i++) {
    const [sx, sy] = toShape(polygon[i]);
    shape.lineTo(sx, sy);
  }
  shape.closePath();
  // Negating y reverses the winding order (clockwise vs anticlockwise).
  // ExtrudeGeometry detects winding itself, so this needs no extra handling.

  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: height,
    bevelEnabled: false,
  });

  const material = new THREE.MeshLambertMaterial({
    color: 0x6e8fa8,
    transparent: true,
    opacity: 0.88,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.rotation.x = -Math.PI / 2;  // shape XY plane → ground XZ plane, +Z → +Y
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  return mesh;
}

/**
 * Return the axis-aligned centre of the polygon (in plan coordinates).
 * Useful for pointing the camera at the building.
 *
 * @param {number[][]} polygon
 * @returns {{x: number, y: number}}
 */
export function polygonCentre(polygon) {
  const xs = polygon.map(p => p[0]);
  const ys = polygon.map(p => p[1]);
  return {
    x: (Math.min(...xs) + Math.max(...xs)) / 2,
    y: (Math.min(...ys) + Math.max(...ys)) / 2,
  };
}
