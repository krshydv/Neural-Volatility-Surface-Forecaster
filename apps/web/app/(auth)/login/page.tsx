"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleGoogleLogin() {
    setError(null);
    setGoogleLoading(true);
    try {
      const { authorization_url } = await api.getGoogleLoginUrl();
      window.location.href = authorization_url;
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Google sign-in is not available right now"
      );
      setGoogleLoading(false);
    }
  }

  return (
    <div>
      <span className="label-tag text-primary mb-2 block">{"// Sign in"}</span>
      <h1 className="font-display text-3xl text-text-primary mb-1">Welcome back</h1>
      <p className="text-sm text-text-secondary mb-6 font-mono">
        Continue your volatility research.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="email" className="label-tag text-text-secondary">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="bg-surface border border-border px-3 py-2.5 text-sm font-mono text-text-primary focus:border-primary outline-none"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="password" className="label-tag text-text-secondary">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="bg-surface border border-border px-3 py-2.5 text-sm font-mono text-text-primary focus:border-primary outline-none"
          />
        </div>

        {error && <p className="text-sm text-danger font-mono">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="btn mt-2 bg-primary text-text-inverse py-3 hover:bg-primary-hover disabled:opacity-50"
        >
          {submitting ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <button
        type="button"
        onClick={handleGoogleLogin}
        disabled={googleLoading}
        className="btn mt-3 w-full border border-border text-text-primary py-3 hover:border-primary transition-colors disabled:opacity-50"
      >
        {googleLoading ? "Redirecting..." : "Continue with Google"}
      </button>

      <p className="mt-6 text-sm text-text-secondary text-center font-mono">
        No account?{" "}
        <Link href="/register" className="text-primary hover:underline">
          Create one
        </Link>
      </p>
    </div>
  );
}
