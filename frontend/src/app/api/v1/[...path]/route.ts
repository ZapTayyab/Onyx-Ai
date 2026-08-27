import { NextRequest, NextResponse } from "next/server";

const BACKEND = "http://backend:8000/v1";

async function handler(
  req: NextRequest,
  { params }: { params: { path: string[] } },
) {
  const path = params.path.join("/");
  const search = req.nextUrl.search;
  const url = `${BACKEND}/${path}${search}`;

  const headers: Record<string, string> = {
    "Content-Type": req.headers.get("Content-Type") || "application/json",
    Authorization: req.headers.get("Authorization") || "",
    "X-Organization-ID": req.headers.get("X-Organization-ID") || "",
  };

  const body =
    req.method !== "GET" && req.method !== "HEAD"
      ? await req.text()
      : undefined;

  const response = await fetch(url, {
    method: req.method,
    headers,
    body,
  });

  return new NextResponse(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: {
      "Content-Type":
        response.headers.get("Content-Type") || "application/json",
    },
  });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
