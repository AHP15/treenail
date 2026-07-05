import { docs } from '@/.source/server';
import { loader } from 'fumadocs-core/source';

// The Fumadocs source loader (D-003) — turns the generated content
// collection into a page tree + page lookup for the /docs route.
export const source = loader({
  baseUrl: '/docs',
  source: docs.toFumadocsSource(),
});
