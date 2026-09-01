import { describe, expect, it } from "vitest";
import { render } from "@testing-library/react";
import { PulseMark } from "@/components/pulse-mark";

describe("PulseMark", () => {
  it("renders an svg waveform", () => {
    const { container } = render(<PulseMark />);
    const svg = container.querySelector("svg");
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveAttribute("viewBox", "0 0 120 32");
  });

  it("applies the animate class by default", () => {
    const { container } = render(<PulseMark />);
    const path = container.querySelector("path");
    expect(path?.getAttribute("class")).toContain("animate-pulse-trace");
  });

  it("omits the animate class when animate is false", () => {
    const { container } = render(<PulseMark animate={false} />);
    const path = container.querySelector("path");
    expect(path?.getAttribute("class")).toBe("");
  });

  it("forwards a custom className to the svg element", () => {
    const { container } = render(<PulseMark className="h-8 w-8" />);
    const svg = container.querySelector("svg");
    expect(svg).toHaveClass("h-8", "w-8");
  });
});
