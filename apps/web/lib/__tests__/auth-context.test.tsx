import { describe, expect, it, vi, beforeEach } from "vitest";
import { act, render, screen, waitFor } from "@testing-library/react";
import { AuthProvider, useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  api: {
    me: vi.fn(),
    login: vi.fn(),
    register: vi.fn(),
    googleCallback: vi.fn(),
  },
}));

function Probe() {
  const { user, token, loading, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="loading">{String(loading)}</span>
      <span data-testid="token">{token ?? "none"}</span>
      <span data-testid="email">{user?.email ?? "none"}</span>
      <button onClick={() => login("a@b.com", "pw")}>login</button>
      <button onClick={logout}>logout</button>
    </div>
  );
}

beforeEach(() => {
  window.localStorage.clear();
  vi.clearAllMocks();
});

describe("AuthProvider", () => {
  it("starts unauthenticated with no stored token", async () => {
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByTestId("loading").textContent).toBe("false"));
    expect(screen.getByTestId("token").textContent).toBe("none");
  });

  it("logs in and stores the token", async () => {
    (api.login as any).mockResolvedValue({
      access_token: "tok123",
      refresh_token: "refresh123",
    });
    (api.me as any).mockResolvedValue({ id: "1", email: "a@b.com" });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByTestId("loading").textContent).toBe("false"));

    await act(async () => {
      screen.getByText("login").click();
    });

    await waitFor(() => expect(screen.getByTestId("token").textContent).toBe("tok123"));
    expect(screen.getByTestId("email").textContent).toBe("a@b.com");
    expect(window.localStorage.getItem("volaris_access_token")).toBe("tok123");
  });

  it("clears the token on logout", async () => {
    (api.login as any).mockResolvedValue({
      access_token: "tok123",
      refresh_token: "refresh123",
    });
    (api.me as any).mockResolvedValue({ id: "1", email: "a@b.com" });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByTestId("loading").textContent).toBe("false"));
    await act(async () => {
      screen.getByText("login").click();
    });
    await waitFor(() => expect(screen.getByTestId("token").textContent).toBe("tok123"));

    await act(async () => {
      screen.getByText("logout").click();
    });

    expect(screen.getByTestId("token").textContent).toBe("none");
    expect(window.localStorage.getItem("volaris_access_token")).toBeNull();
  });
});
