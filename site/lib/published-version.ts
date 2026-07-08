// The last published npm release of `treenail` (R-009, T-017).
//
// Install-critical docs surfaces — the quickstart `npx` commands, the install
// steps, and the CLI command reference — render their version and the
// release-tracking note from THIS pinned value. It is deliberately NOT read
// from the product's `cli/package.json`: that is "raw main", which runs ahead
// of the last publish between releases, and pinning to it would advertise
// behavior a first-run user cannot yet `npx treenail install` (R-009). The
// unversioned narrative/conceptual pages keep tracking main per D-014; only
// this sharp install-critical edge is pinned.
//
// RELEASE STEP: bump PUBLISHED_VERSION in the same change that publishes the
// new version to npm. The failure mode is deliberately safe — if this pin
// lags an actual publish, the install-critical pages point at an OLDER release
// than is live (under-claiming) and the "newest changes may be ahead" note
// stays true. It can never produce the R-009 harm of documenting a release
// that isn't installable yet.
export const PUBLISHED_VERSION = '0.0.1';

// The disclosure note shown on install-critical pages (R-009): the docs track
// the latest *release*, and main may already be ahead of it.
export const releaseTrackingNote =
  `Docs track the latest release (v${PUBLISHED_VERSION}); newest changes may be ahead.`;
