import { defineDocs, defineConfig } from 'fumadocs-mdx/config';

// Documentation collection (D-003). MDX lives under content/docs as a
// single, unversioned set (D-014). Build-time derived pages (T-003) are
// generated into this same tree.
export const docs = defineDocs({
  dir: 'content/docs',
});

export default defineConfig();
