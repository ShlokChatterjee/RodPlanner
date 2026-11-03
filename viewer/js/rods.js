import * as THREE from 'three';
import { planToWorld } from './coords.js';

const ROD_COLOUR  = 0xffd700;  // gold
const CONE_COLOUR = 0x4499ff;  // blue

/**
 * Build a THREE.Group containing all rod cylinders and protection cones.
 *
 * Positions go through planToWorld (see coords.js), the same mapping the
 * building uses. Rods stand ON the roof: rod.height is measured from the
 * roof surface (see rodplanner/placement/models.py), so the rod base sits
 * at roofHeight and its tip at roofHeight + rod.height.
 *
 * @param {Array<{x:number, y:number, height:number, radius:number}>} rods
 * @param {number} roofHeight  height of the flat roof above the ground, metres
 * @returns {THREE.Group}
 */
export function buildRods(rods, roofHeight) {
  const group = new THREE.Group();

  const rodMaterial = new THREE.MeshLambertMaterial({ color: ROD_COLOUR });
  const coneMaterial = new THREE.MeshLambertMaterial({
    color: CONE_COLOUR,
    transparent: true,
    opacity: 0.12,
    side: THREE.DoubleSide,  // visible from inside the cone too
    depthWrite: false,       // overlapping transparent cones don't hide each other
  });

  for (const rod of rods) {
    // Both meshes are centred on their own middle, so we place that middle
    // half a rod-height above the roof.
    const mid = planToWorld(rod.x, rod.y, roofHeight + rod.height / 2);

    // ── rod cylinder ──────────────────────────────────────────────────────
    const rodGeo = new THREE.CylinderGeometry(0.07, 0.07, rod.height, 8);
    const rodMesh = new THREE.Mesh(rodGeo, rodMaterial);
    rodMesh.position.set(mid.x, mid.y, mid.z);
    rodMesh.castShadow = true;
    rodMesh.userData.plan = { x: rod.x, y: rod.y };
    group.add(rodMesh);

    // ── protection cone ───────────────────────────────────────────────────
    // ConeGeometry: apex at +height/2, base at -height/2. Centred at `mid`,
    // the apex is at the rod tip and the base circle lies on the roof, with
    // the protection radius computed by the backend.
    const coneGeo = new THREE.ConeGeometry(rod.radius, rod.height, 32, 1, true);
    const coneMesh = new THREE.Mesh(coneGeo, coneMaterial);
    coneMesh.position.set(mid.x, mid.y, mid.z);
    group.add(coneMesh);
  }

  return group;
}
