"use client";

export function PulseMark({
  className = "",
  animate = true,
  inverse = false,
}: {
  className?: string;
  animate?: boolean;
  inverse?: boolean;
}) {
  return (
    <svg
      viewBox="0 0 120 32"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M2 16 L20 16 L26 6 L34 26 L42 10 L48 22 L54 16 L64 16 L70 4 L78 28 L86 12 L92 20 L98 16 L118 16"
        stroke={inverse ? "var(--color-text-inverse)" : "var(--color-primary)"}
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={animate ? "animate-pulse-trace" : ""}
      />
    </svg>
  );
}
