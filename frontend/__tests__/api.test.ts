/**
 * Unit tests for the centralised API client (api.ts).
 * We mock global fetch so no real HTTP calls are made.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";

// Minimal localStorage stub
const storage: Record<string, string> = {};
vi.stubGlobal("localStorage", {
  getItem: (key: string) => storage[key] ?? null,
  setItem: (key: string, val: string) => { storage[key] = val; },
  removeItem: (key: string) => { delete storage[key]; },
});

// Stub fetch before importing api
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

import { api } from "../src/lib/api";

function makeResponse(body: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(typeof body === "string" ? body : JSON.stringify(body)),
  } as Response;
}

beforeEach(() => {
  mockFetch.mockReset();
  storage["snt_auth_token"] = "test-token";
});

describe("api.evaluations", () => {
  it("list sends Authorization header", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse([]));
    await api.evaluations.list("org-1");
    const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect((init.headers as Record<string, string>)["Authorization"]).toBe("Bearer test-token");
  });

  it("list throws on 401", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse({ detail: "Unauthorized" }, 401));
    await expect(api.evaluations.list("org-1")).rejects.toThrow("Session expired");
  });

  it("getReport fetches plain text with correct format param", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse("SNT AI Evaluation Report\n====="));
    const text = await api.evaluations.getReport("run-abc", "summary");
    expect(text).toContain("SNT AI");
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toMatch(/format=summary/);
  });

  it("getReport throws on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse("", 404));
    await expect(api.evaluations.getReport("run-xyz")).rejects.toThrow("Report fetch failed");
  });
});

describe("api.org", () => {
  it("get fetches /organizations/me", async () => {
    mockFetch.mockResolvedValueOnce(makeResponse({ id: "org-1", name: "Demo" }));
    const org = await api.org.get();
    expect(org.name).toBe("Demo");
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toMatch(/organizations\/me/);
  });
});
