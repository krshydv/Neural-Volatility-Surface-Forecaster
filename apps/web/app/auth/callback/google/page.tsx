"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";

function GoogleCallbackInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { loginWithGoogleCode } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) {
      setError("Missing authorization code from Google");
      return;
    }
    loginWithGoogleCode(code)
      .then(() => router.push("/dashboard"))
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Google sign-in failed")
      );
  }, [searchParams, loginWithGoogleCode, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink">
      <p className="text-sm text-text-secondary">
        {error ?? "Finishing Google sign-in..."}
      </p>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense fallback={null}>
      <GoogleCallbackInner />
    </Suspense>
  );
}
