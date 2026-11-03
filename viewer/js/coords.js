/**
 * The one place that decides how plan coordinates become 3D world coordinates.
 *
 * Plan space (what the API returns, in metres):
 *   x → right, y → DOWN the image (OpenCV pixel convention, see
 *   rodplanner/vision/extractor.py). No y-flip is applied in the backend.
 *
 * World space (Three.js, right-handed, Y up):
 *   x → right, y → up, z → towards the default camera.
 *
 * Mapping:  plan (x, y), elevation h  →  world (x, h, y)
 *
 * Seen from above (camera looking straight down, screen-up = world -z),
 * world +z points down the screen, exactly like image rows. So the 3D top
 * view looks like the input image, not a mirror of it.
 *
 * Every module that places something in the scene (building, rods, camera)
 * must go through this function. The bug this file fixes was two modules
 * each doing their own mapping and disagreeing about the sign of z.
 *
 * @param {number} x  plan x in metres
 * @param {number} y  plan y in metres
 * @param {number} [h=0]  elevation above the ground in metres
 * @returns {{x: number, y: number, z: number}}
 */
export function planToWorld(x, y, h = 0) {
  return { x, y: h, z: y };
}
