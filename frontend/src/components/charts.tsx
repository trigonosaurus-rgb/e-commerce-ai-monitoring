"use client";

import { useMemo } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { money } from "@/lib/format";
import type { HistorySeries } from "@/lib/types";

/** Color follows the entity: your store is slot 1, competitors take the next slots in
 *  offer-id order, so a series never changes color when others are added or hidden. */
export function seriesColors(offers: { id: number; is_own: boolean }[]): Map<number, string> {
  const map = new Map<number, string>();
  const own = offers.find((o) => o.is_own);
  if (own) map.set(own.id, "var(--series-1)");
  offers
    .filter((o) => !o.is_own)
    .sort((a, b) => a.id - b.id)
    .forEach((o, i) => map.set(o.id, `var(--series-${Math.min(i + 2, 7)})`));
  return map;
}

export function Swatch({ color }: { color?: string }) {
  return <span className="inline-block h-0.5 w-3 shrink-0 rounded-full" style={{ background: color }} />;
}

type Row = { t: number } & Record<string, number | undefined>;

function ChartTooltip({
  active,
  payload,
  label,
  currency,
  names,
}: {
  active?: boolean;
  payload?: readonly { dataKey?: unknown; value?: unknown; color?: string }[];
  label?: unknown;
  currency: string | null;
  names: Map<string, string>;
}) {
  if (!active || !payload?.length) return null;
  const rows = [...payload].sort((a, b) => Number(a.value) - Number(b.value));
  return (
    <div className="min-w-44 rounded-lg border bg-popover px-3 py-2 text-xs shadow-md">
      <div className="mb-1.5 font-medium text-muted-foreground">
        {new Date(Number(label)).toLocaleString("en-GB", {
          day: "numeric",
          month: "short",
          hour: "2-digit",
          minute: "2-digit",
        })}
      </div>
      <div className="grid gap-1">
        {rows.map((item) => (
          <div key={String(item.dataKey)} className="flex items-center gap-2">
            <Swatch color={item.color} />
            <span className="flex-1 truncate">{names.get(String(item.dataKey))}</span>
            <span className="font-medium tabular">{money(Number(item.value), currency)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function PriceChart({ series, currency }: { series: HistorySeries[]; currency: string | null }) {
  const colors = useMemo(
    () => seriesColors(series.map((s) => ({ id: s.offer_id, is_own: s.is_own }))),
    [series],
  );
  const { rows, names } = useMemo(() => {
    const byTime = new Map<number, Row>();
    const names = new Map<string, string>();
    for (const s of series) {
      const key = `o${s.offer_id}`;
      names.set(key, s.is_own ? `${s.store} (you)` : s.store);
      for (const p of s.points) {
        if (p.flagged) continue; // readings waiting for review are not drawn as facts
        // readings of one check run land within seconds: bucket them per minute
        const t = Math.round(new Date(p.t).getTime() / 60_000) * 60_000;
        const row = byTime.get(t) ?? { t };
        row[key] = p.price;
        byTime.set(t, row);
      }
    }
    return { rows: [...byTime.values()].sort((a, b) => a.t - b.t), names };
  }, [series]);

  const visible = series.filter((s) => s.points.some((p) => !p.flagged));
  if (rows.length < 2) {
    return (
      <div className="flex h-64 items-center justify-center rounded-lg bg-muted/40 text-sm text-muted-foreground">
        The chart appears after the second price check.
      </div>
    );
  }
  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-x-4 gap-y-1.5 text-xs">
        {visible.map((s) => (
          <span key={s.offer_id} className="inline-flex items-center gap-1.5">
            <Swatch color={colors.get(s.offer_id)} />
            <span className={s.is_own ? "font-medium" : "text-muted-foreground"}>
              {s.is_own ? `${s.store} (you)` : s.store}
            </span>
          </span>
        ))}
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={rows} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--border)" />
            <XAxis
              dataKey="t"
              type="number"
              scale="time"
              domain={["dataMin", "dataMax"]}
              tickFormatter={(t) =>
                new Date(t).toLocaleDateString("en-GB", { day: "numeric", month: "short" })
              }
              tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "var(--border)" }}
              minTickGap={32}
            />
            <YAxis
              width={64}
              domain={["auto", "auto"]}
              tickFormatter={(v) => money(v, currency).replace(/\.00$/, "")}
              tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              content={({ active, payload, label }) => (
                <ChartTooltip
                  active={active}
                  payload={payload}
                  label={label}
                  currency={currency}
                  names={names}
                />
              )}
              cursor={{ stroke: "var(--muted-foreground)", strokeWidth: 1 }}
            />
            {visible.map((s) => (
              <Line
                key={s.offer_id}
                dataKey={`o${s.offer_id}`}
                type="monotone"
                stroke={colors.get(s.offer_id)}
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
                dot={false}
                activeDot={{ r: 4, strokeWidth: 2, stroke: "var(--card)" }}
                connectNulls
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

/** Tiny trend of the cheapest competitor price; one series, so no legend. */
export function Sparkline({ values }: { values: (number | null)[] }) {
  const points = values.filter((v): v is number => v !== null);
  if (points.length < 2) return <span className="text-xs text-muted-foreground">—</span>;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const span = max - min || 1;
  const path = points
    .map((v, i) => `${(i / (points.length - 1)) * 80},${22 - ((v - min) / span) * 18}`)
    .join(" L");
  const falling = points[points.length - 1] < points[0];
  return (
    <svg viewBox="0 0 80 24" className="h-6 w-20" aria-hidden>
      <path
        d={`M${path}`}
        fill="none"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={falling ? "stroke-destructive" : "stroke-muted-foreground"}
      />
    </svg>
  );
}
