import * as THREE from 'three';

const ROD_COLOUR  = 0xffd700;  // gold
const CONE_COLOUR = 0x4499ff;  // blue

/**
 * Build a THREE.Group containing all rod cylinders and protection cones.
 *
 * Coordinate mapping from plan space to world space:
 *   plan x  → world x
 *   plan y  → world z   (plan "forward" = world "depth")
 *   height  → world y   (upward)
 *
 * @param {Array<{x:number, y:number, height:number, radius:number}>} rods
 * @returns {THREE.Group}
 */
export function buildRods(rods) {
  const group = new THREE.Group();

  const rodMaterial = new THREE.MeshLambertMaterial({ color: ROD_COLOUR });
  const coneMaterial = new THREE.MeshLambertMaterial({
    color: CONE_COLOUR,
    transparent: true,
    opacity: 0.12,
    side: THREE.DoubleSide,  // visible from inside the cone too
  });

  for (const rod of rods) {
    // ── rod cylinder ──────────────────────────────────────────────────────
    const rodGeo = new THREE.CylinderGeometry(0.07, 0.07, rod.height, 8);
    const rodMesh = new THREE.Mesh(rodGeo, rodMaterial);
    // CylinderGeometry is centred at origin; shift up so base is at y=0
    rodMesh.position.set(rod.x, rod.height / 2, rod.y);
    rodMesh.castShadow = true;
    group.add(rodMesh);

    // ── protection cone ───────────────────────────────────────────────────
    // ConeGeometry: apex at top, base at bottom by default.
    // We want apex at the rod tip (y = rod.height) and base at y = 0.
    const coneGeo = new THREE.ConeGeometry(rod.radius, rod.height, 32, 1, true);
    const coneMesh = new THREE.Mesh(coneGeo, coneMaterial);
    // ConeGeometry centre is at half-height; position so apex = rod.height
    coneMesh.position.set(rod.x, rod.height / 2, rod.y);
    group.add(coneMesh);
  }

  return group;
}
