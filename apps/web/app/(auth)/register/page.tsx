"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(email, password, fullName || undefined);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <span className="label-tag text-primary mb-2 block">{"// Create account"}</span>
      <h1 className="font-display text-3xl text-text-primary mb-1">Get started</h1>
      <p className="text-sm text-text-secondary mb-6 font-mono">
        Set up your research workspace.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="fullName" className="label-tag text-text-secondary">
            Full name
          </label>
          <input
            id="fullName"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="bg-surface border border-border px-3 py-2.5 text-sm font-mono text-text-primary focus:border-primary outline-none"
          />
        </div>

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
            minLength={8}
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
          {submitting ? "Creating account..." : "Create account"}
        </button>
      </form>

      <p className="mt-6 text-sm text-text-secondary text-center font-mono">
        Already have an account?{" "}
        <Link href="/login" className="text-primary hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
