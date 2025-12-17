import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const body = await req.text();

  const authHeader = req.headers.get("authorization") || "";

  const res = await fetch(
    "http://13.235.69.89:8080/agent-run",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: authHeader,
      },
      body,
    }
  );

  const data = await res.text();

  return new NextResponse(data, {
    status: res.status,
    headers: {
      "Content-Type": res.headers.get("content-type") || "application/json",
    },
  });
}
