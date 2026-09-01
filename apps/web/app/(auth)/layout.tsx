import Link from "next/link";
import { PulseMark } from "@/components/pulse-mark";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-surface-muted px-4">
      <Link href="/" className="flex items-center gap-3 mb-10">
        <PulseMark className="h-5 w-16" animate={false} />
        <span className="label-tag text-text-primary">Hermes Forecast</span>
      </Link>
      <div className="w-full max-w-sm bg-surface border border-border p-8">
        {children}
      </div>
    </main>
  );
}
