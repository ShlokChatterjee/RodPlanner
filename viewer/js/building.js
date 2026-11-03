import * as THREE from 'three';

/**
 * Build an extruded mesh from a polygon footprint.
 *
 * @param {number[][]} polygon  Array of [x, y] pairs in metres (plan coordinates)
 * @param {number}     height   Building height in metres
 * @returns {THREE.Mesh}
 */
export function buildBuilding(polygon, height) {
  const shape = new THREE.Shape();
  // Plan coords: x→right, y→forward.  ExtrudeGeometry works in XY, so we
  // use plan-x as shape-x and plan-y as shape-y, then rotate the mesh.
  shape.moveTo(polygon[0][0], polygon[0][1]);
  for (let i = 1; i < polygon.length; i++) {
    shape.lineTo(polygon[i][0], polygon[i][1]);
  }
  shape.closePath();

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
  // Rotate so the shape lies flat on the XZ plane and extrudes upward (Y).
  // ExtrudeGeometry extrudes along +Z by default; after rotation +Z→+Y.
  mesh.rotation.x = -Math.PI / 2;
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
