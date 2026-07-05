import { source } from '@/lib/source';
import { createFromSource } from 'fumadocs-core/search/server';

// Built-in Fumadocs search over the docs content (D-003). Ancillary
// search/analytics defaults are finalized in T-006; this is the default
// static index the docs shell's search dialog queries.
export const { GET } = createFromSource(source);
