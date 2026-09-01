"use client";

interface HeatmapProps {
  rows: number[];
  cols: number[];
  grid: number[][];
  rowLabel: string;
  colLabel: string;
  onCellHover?: (rowIndex: number, colIndex: number) => void;
}

function colorFor(value: number, min: number, max: number): string {
  const t = max > min ? (value - min) / (max - min) : 0.5;
  const hue = 210 - t * 190;
  const lightness = 22 + t * 30;
  return `hsl(${hue}, 65%, ${lightness}%)`;
}

export function VolSurfaceHeatmap({ rows, cols, grid, rowLabel, colLabel, onCellHover }: HeatmapProps) {
  const flat = grid.flat();
  const min = Math.min(...flat);
  const max = Math.max(...flat);

  const cellWidth = 560 / cols.length;
  const cellHeight = 320 / rows.length;

  return (
    <div className="overflow-x-auto">
      <svg viewBox="0 0 620 360" className="w-full max-w-3xl">
        <text x="0" y="12" className="fill-text-tertiary text-[9px] font-mono">
          {rowLabel} ↓ / {colLabel} →
        </text>
        <g transform="translate(40, 20)">
          {grid.map((row, rowIndex) =>
            row.map((value, colIndex) => (
              <rect
                key={`${rowIndex}-${colIndex}`}
                x={colIndex * cellWidth}
                y={rowIndex * cellHeight}
                width={cellWidth}
                height={cellHeight}
                fill={colorFor(value, min, max)}
                onMouseEnter={() => onCellHover?.(rowIndex, colIndex)}
              >
                <title>{`${rowLabel}=${rows[rowIndex].toFixed(2)} ${colLabel}=${cols[colIndex].toFixed(2)} IV=${(value * 100).toFixed(1)}%`}</title>
              </rect>
            ))
          )}
        </g>
      </svg>
      <div className="flex items-center gap-2 mt-2 text-[10px] font-mono text-text-tertiary">
        <span>{(min * 100).toFixed(1)}%</span>
        <div
          className="h-2 flex-1 rounded-sm"
          style={{ background: "linear-gradient(90deg, hsl(210,65%,22%), hsl(20,65%,52%))" }}
        />
        <span>{(max * 100).toFixed(1)}%</span>
      </div>
    </div>
  );
}
