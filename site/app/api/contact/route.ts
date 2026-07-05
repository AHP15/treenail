import { NextResponse } from 'next/server';
import { handleContact } from '@/lib/forms/handlers';

// Contact endpoint (D-006, D-002): thin adapter over the framework-agnostic
// handler core in lib/forms/handlers.ts. Validate → hand off to the
// transactional-email provider. Stores nothing.
export async function POST(request: Request): Promise<Response> {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body.' }, { status: 400 });
  }
  const result = await handleContact(body);
  return NextResponse.json(result.json, { status: result.status });
}
