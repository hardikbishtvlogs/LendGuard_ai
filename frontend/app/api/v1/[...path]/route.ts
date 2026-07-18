import {NextRequest} from "next/server";

const BACKEND = process.env.BACKEND_INTERNAL_URL || "http://127.0.0.1:8000";

async function proxy(request: NextRequest, context: {params: Promise<{path: string[]}>}) {
  const params = await context.params;
  const path = params.path.join("/");
  const target = new URL(`/api/v1/${path}${request.nextUrl.search}`, BACKEND);
  const headers = new Headers();

  for (const key of ["authorization", "content-type", "accept"]) {
    const value = request.headers.get(key);
    if (value) headers.set(key, value);
  }

  const hasBody = !["GET", "HEAD"].includes(request.method);
  const body = hasBody ? await request.arrayBuffer() : undefined;
  const response = await fetch(target, {
    method: request.method,
    headers,
    body: body && body.byteLength > 0 ? body : undefined,
    cache: "no-store",
  });

  const responseHeaders = new Headers();
  const contentType = response.headers.get("content-type");
  const disposition = response.headers.get("content-disposition");
  if (contentType) responseHeaders.set("content-type", contentType);
  if (disposition) responseHeaders.set("content-disposition", disposition);

  if (response.status === 204 || response.status === 304) {
    return new Response(null, {status: response.status, headers: responseHeaders});
  }

  return new Response(await response.arrayBuffer(), {status: response.status, headers: responseHeaders});
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
