import { describe, expect, it } from "vitest";
import { render } from "@testing-library/react";
import { LineChart } from "@/components/line-chart";

describe("LineChart", () => {
  const baseProps = {
    xValues: [0, 1, 2, 3],
    xLabel: "Days ahead",
    yLabel: "Volatility",
  };

  it("renders one polyline per series", () => {
    const { container } = render(
      <LineChart
        {...baseProps}
        series={[
          { name: "Forecast", color: "#e3a53d", yValues: [0.2, 0.22, 0.25, 0.21] },
          { name: "Upper", color: "#8a94a6", yValues: [0.25, 0.27, 0.3, 0.26] },
        ]}
      />
    );
    const polylines = container.querySelectorAll("polyline");
    expect(polylines.length).toBe(2);
  });

  it("renders a single svg with the expected viewBox", () => {
    const { container } = render(
      <LineChart {...baseProps} series={[{ name: "A", color: "#fff", yValues: [1, 2, 3, 4] }]} />
    );
    const svg = container.querySelector("svg");
    expect(svg).toHaveAttribute("viewBox", "0 0 560 260");
  });

  it("handles a flat series (yMin === yMax) without throwing", () => {
    expect(() =>
      render(
        <LineChart {...baseProps} series={[{ name: "Flat", color: "#fff", yValues: [1, 1, 1, 1] }]} />
      )
    ).not.toThrow();
  });
});
