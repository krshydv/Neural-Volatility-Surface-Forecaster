"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { WorkspaceStateProvider } from "@/lib/workspace-state-context";
import { Sidebar } from "@/components/sidebar";
import { PulseMark } from "@/components/pulse-mark";
import { CommandPalette } from "@/components/command-palette";
import { TopBar } from "@/components/top-bar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <PulseMark className="h-6 w-24" />
      </div>
    );
  }

  return (
    <WorkspaceStateProvider>
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <div className="flex-1 min-w-0 flex flex-col">
          <TopBar />
          <div className="flex-1 min-w-0">{children}</div>
        </div>
      </div>
      <CommandPalette />
    </WorkspaceStateProvider>
  );
}
