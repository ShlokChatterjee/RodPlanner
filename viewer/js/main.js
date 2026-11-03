import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { buildBuilding, polygonCentre } from './building.js';
import { buildRods } from './rods.js';

// ── load data ────────────────────────────────────────────────────────────────

const data = await fetch('./sample_output.json').then(r => r.json());

// ── renderer ─────────────────────────────────────────────────────────────────

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ── scene ────────────────────────────────────────────────────────────────────

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0f1117);
scene.fog = new THREE.FogExp2(0x0f1117, 0.018);

// ── camera ───────────────────────────────────────────────────────────────────

const camera = new THREE.PerspectiveCamera(
  55, window.innerWidth / window.innerHeight, 0.1, 300
);

// Point the camera at the building centre, offset at an angle
const centre = polygonCentre(data.polygon);
camera.position.set(centre.x + 20, 18, centre.y + 20);
camera.lookAt(centre.x, 0, centre.y);

// ── orbit controls ───────────────────────────────────────────────────────────

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(centre.x, 0, centre.y);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 5;
controls.maxDistance = 120;
controls.maxPolarAngle = Math.PI / 2.05;  // stop camera going below ground

// ── lights ───────────────────────────────────────────────────────────────────

scene.add(new THREE.AmbientLight(0xffffff, 0.45));

const sun = new THREE.DirectionalLight(0xfff5e0, 1.1);
sun.position.set(25, 40, 20);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 120;
sun.shadow.camera.left = -40;
sun.shadow.camera.right = 40;
sun.shadow.camera.top = 40;
sun.shadow.camera.bottom = -40;
scene.add(sun);

// Soft fill from the opposite side
const fill = new THREE.DirectionalLight(0xc0d8ff, 0.35);
fill.position.set(-15, 20, -10);
scene.add(fill);

// ── ground + grid ────────────────────────────────────────────────────────────

const groundGeo = new THREE.PlaneGeometry(200, 200);
const groundMat = new THREE.MeshLambertMaterial({ color: 0x1a2a20 });
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

const gridSize = Math.max(...data.polygon.flat()) + 20;
const grid = new THREE.GridHelper(gridSize * 2, gridSize * 2, 0x2a3a30, 0x1e2e24);
grid.position.y = 0.01;  // tiny offset to avoid z-fighting with ground
scene.add(grid);

// ── building + rods ──────────────────────────────────────────────────────────

const buildingHeight = data.rods.length > 0 ? data.rods[0].height : 3.0;
scene.add(buildBuilding(data.polygon, buildingHeight));
scene.add(buildRods(data.rods));

// ── stats overlay ─────────────────────────────────────────────────────────────

document.getElementById('stat-rods').textContent =
  `rods: ${data.rod_count}`;
document.getElementById('stat-coverage').textContent =
  `coverage: ${(data.coverage_fraction * 100).toFixed(1)} %`;
document.getElementById('stat-area').textContent =
  `area: ${data.area_m2} m²`;

// ── resize handler ───────────────────────────────────────────────────────────

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ── animation loop ───────────────────────────────────────────────────────────

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
