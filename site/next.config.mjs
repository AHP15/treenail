import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const nextConfig = {
  turbopack: {
    // Pin the workspace root to site/ — the repo has sibling lockfiles
    // (cli/, and a stray parent one) that Next would otherwise infer from.
    root: import.meta.dirname,
  },
  // Build-time single-sourcing (T-003) reads sibling repo files at build
  // time thanks to D-004's monorepo layout.
};

export default withMDX(nextConfig);
