"use client";

interface LineChartProps {
  xValues: number[];
  series: { name: string; color: string; yValues: number[] }[];
  xLabel: string;
  yLabel: string;
  yAsPercent?: boolean;
}

export function LineChart({ xValues, series, xLabel, yLabel, yAsPercent }: LineChartProps) {
  const width = 560;
  const height = 260;
  const padding = { top: 16, right: 16, bottom: 32, left: 48 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const allY = series.flatMap((s) => s.yValues);
  const yMin = Math.min(...allY);
  const yMax = Math.max(...allY);
  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);

  function px(x: number) {
    return padding.left + (xMax > xMin ? ((x - xMin) / (xMax - xMin)) * plotWidth : plotWidth / 2);
  }

  function py(y: number) {
    return (
      padding.top + plotHeight - (yMax > yMin ? ((y - yMin) / (yMax - yMin)) * plotHeight : plotHeight / 2)
    );
  }

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full max-w-2xl">
      <line
        x1={padding.left}
        y1={padding.top}
        x2={padding.left}
        y2={height - padding.bottom}
        stroke="var(--color-line)"
      />
      <line
        x1={padding.left}
        y1={height - padding.bottom}
        x2={width - padding.right}
        y2={height - padding.bottom}
        stroke="var(--color-line)"
      />

      <text x={padding.left} y={12} className="fill-text-tertiary text-[9px] font-mono">
        {yAsPercent ? `${(yMax * 100).toFixed(1)}%` : yMax.toFixed(3)}
      </text>
      <text x={padding.left} y={height - padding.bottom + 10} className="fill-text-tertiary text-[9px] font-mono">
        {yAsPercent ? `${(yMin * 100).toFixed(1)}%` : yMin.toFixed(3)}
      </text>

      <text
        x={width / 2}
        y={height - 4}
        textAnchor="middle"
        className="fill-text-tertiary text-[9px] font-mono uppercase tracking-wide"
      >
        {xLabel}
      </text>
      <text
        x={12}
        y={height / 2}
        textAnchor="middle"
        transform={`rotate(-90, 12, ${height / 2})`}
        className="fill-text-tertiary text-[9px] font-mono uppercase tracking-wide"
      >
        {yLabel}
      </text>

      {series.map((s) => (
        <polyline
          key={s.name}
          fill="none"
          stroke={s.color}
          strokeWidth={2}
          points={xValues.map((x, i) => `${px(x)},${py(s.yValues[i])}`).join(" ")}
        />
      ))}
    </svg>
  );
}
