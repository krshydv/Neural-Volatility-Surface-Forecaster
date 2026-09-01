import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "Hermes Forecast — Neural Volatility Intelligence",
  description: "Implied volatility surfaces, options analytics, and neural forecasting.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-background text-text-primary font-mono">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
