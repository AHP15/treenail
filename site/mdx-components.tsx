import defaultMdxComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';
import { ReleaseNote } from '@/app/components/release-note';

// Central MDX component map for docs pages (D-003). Extend here as the
// authored docs sections (T-009+) introduce custom components.
export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    // Install-critical release-tracking disclosure (R-009, T-017).
    ReleaseNote,
    ...components,
  };
}
