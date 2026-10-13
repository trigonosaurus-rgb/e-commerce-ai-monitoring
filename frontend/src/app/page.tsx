"use client";

import { Bell, Bot, ChevronRight, CircleAlert, Radar, ScanSearch, ShieldCheck } from "lucide-react";
import Link from "next/link";

import { AddProductButton } from "@/components/app-shell";
import { Sparkline } from "@/components/charts";
import {
  EmptyState,
  LoadingBlock,
  PageHeader,
  PositionBadge,
  QueryError,
  RunStatusBadge,
} from "@/components/common";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { money, timeAgo, usd } from "@/lib/format";
import { useAlerts, useDashboard, useMe, useProducts, useRuns } from "@/lib/queries";
import type { ProductSummary } from "@/lib/types";

function Kpi({ label, value, hint }: { label: string; value: React.ReactNode; hint?: string }) {
  return (
    <Card size="sm">
      <CardContent>
        <div className="text-xs text-muted-foreground">{label}</div>
        <div className="mt-1 text-2xl font-semibold tracking-tight">{value}</div>
        {hint && <div className="mt-0.5 text-xs text-muted-foreground">{hint}</div>}
      </CardContent>
    </Card>
  );
}

function ProductRow({ product }: { product: ProductSummary }) {
  const p = product.position;
  return (
    <Link
      href={`/product/?id=${product.id}`}
      className="group grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-2 px-4 py-3.5 transition-colors hover:bg-muted/50 md:grid-cols-[minmax(0,2fr)_1fr_1fr_150px_16px] lg:grid-cols-[minmax(0,2.2fr)_1fr_1fr_80px_150px_16px]"
    >
      <div className="flex min-w-0 items-center gap-3">
        <div className="flex size-11 shrink-0 items-center justify-center overflow-hidden rounded-lg border bg-white">
          {product.image_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={product.image_url} alt="" className="size-full object-contain" loading="lazy" />
          ) : (
            <Radar className="size-5 text-muted-foreground" />
          )}
        </div>
        <div className="min-w-0">
          <div className="truncate font-medium">{product.name}</div>
          <div className="flex flex-wrap items-center gap-x-2 text-xs text-muted-foreground">
            <span>{product.tracking} competitor{product.tracking === 1 ? "" : "s"}</span>
            {product.proposed > 0 && (
              <Badge className="h-4 bg-primary/12 px-1.5 text-[10px] text-primary">
                {product.proposed} to review
              </Badge>
            )}
            {product.attention > 0 && (
              <span className="inline-flex items-center gap-0.5 text-warning">
                <CircleAlert className="size-3" /> {product.attention} need attention
              </span>
            )}
          </div>
        </div>
      </div>
      <div className="hidden md:block">
        <div className="text-[11px] text-muted-foreground">Your price</div>
        <div className="font-medium tabular">{money(p.own_price, product.currency)}</div>
      </div>
      <div className="hidden md:block">
        <div className="text-[11px] text-muted-foreground">Cheapest rival</div>
        <div className="truncate font-medium tabular">
          {money(p.lowest, product.currency)}
          {product.lowest_store && (
            <span className="ml-1 text-xs font-normal text-muted-foreground">{product.lowest_store}</span>
          )}
        </div>
      </div>
      <div className="hidden lg:block" title="Cheapest competitor, last 14 days">
        <Sparkline values={product.trend.map((t) => t.lowest)} />
      </div>
      <div className="justify-self-end">
        <PositionBadge position={p} />
      </div>
      <ChevronRight className="hidden size-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 md:block" />
    </Link>
  );
}

function HowItWorks() {
  const steps = [
    { icon: ScanSearch, title: "Paste your product link", text: "The agent reads your page: model, EAN and price." },
    { icon: Bot, title: "The agent finds rivals", text: "It searches your market, screens results and verifies each store's price. You approve the matches." },
    { icon: ShieldCheck, title: "Prices you can audit", text: "Scheduled checks store every price with the page fragment it came from. Changes trigger alerts." },
  ];
  return (
    <div className="grid gap-3 md:grid-cols-3">
      {steps.map(({ icon: Icon, title, text }, i) => (
        <Card key={title} size="sm">
          <CardContent className="flex gap-3">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Icon className="size-4" />
            </span>
            <div>
              <div className="text-sm font-medium">
                <span className="text-muted-foreground">{i + 1}.</span> {title}
              </div>
              <div className="mt-0.5 text-xs text-muted-foreground">{text}</div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const { data: me } = useMe();
  const dashboard = useDashboard();
  const products = useProducts();
  const runs = useRuns();
  const alerts = useAlerts();
  const d = dashboard.data;

  return (
    <>
      <PageHeader
        title="Dashboard"
        description={
          me?.demo
            ? "Live demo: product pages of real German shops play the role of “your store”. Prices and agent runs are real."
            : "Where your prices stand against the market right now."
        }
        actions={<AddProductButton />}
      />

      {d && d.products > 0 && (
        <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-5">
          <Kpi label="Products" value={d.products} hint={`${d.competitors} competitor pages`} />
          <Kpi
            label="You're cheapest"
            value={`${d.positions.cheapest ?? 0} / ${d.products}`}
            hint={`${d.positions.above_market ?? 0} above market`}
          />
          <Kpi label="Alerts · 7 days" value={d.alerts_7d} hint={`${d.unread_alerts} unread`} />
          <Kpi label="Price checks · 7 days" value={d.checks_7d} hint={`last ${timeAgo(d.last_check_at)}`} />
          <Kpi label="AI cost · 30 days" value={usd(d.cost_30d_usd)} hint="all agent runs" />
        </div>
      )}

      {products.error ? (
        <QueryError error={products.error} retry={() => products.refetch()} />
      ) : !products.data ? (
        <LoadingBlock />
      ) : products.data.length === 0 ? (
        <div className="grid gap-6">
          <EmptyState
            icon={Radar}
            title={me?.demo ? "The demo data is being prepared" : "No products yet"}
            action={<AddProductButton />}
          >
            {me?.demo
              ? "Real price history is being collected. Meanwhile, see how it works below."
              : "Add a product page from your store and the agent will find where else it is sold."}
          </EmptyState>
          <HowItWorks />
        </div>
      ) : (
        <Card className="gap-0 py-0">
          <div className="divide-y">
            {products.data.map((product) => (
              <ProductRow key={product.id} product={product} />
            ))}
          </div>
        </Card>
      )}

      {(runs.data?.length || alerts.data?.items.length) ? (
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Agent activity</CardTitle>
              <Link href="/activity/" className="text-xs text-muted-foreground hover:text-foreground">
                View all
              </Link>
            </CardHeader>
            <CardContent className="grid gap-1">
              {runs.data?.slice(0, 5).map((run) => (
                <Link
                  key={run.id}
                  href={`/run/?id=${run.id}`}
                  className="flex min-w-0 items-center gap-3 rounded-lg px-2 py-2 text-sm hover:bg-muted/60"
                >
                  {run.kind === "discovery" ? (
                    <Bot className="size-4 shrink-0 text-primary" />
                  ) : (
                    <Radar className="size-4 shrink-0 text-muted-foreground" />
                  )}
                  <span className="min-w-0 flex-1">
                    <span className="block truncate">{run.title}</span>
                    <span className="block truncate text-xs text-muted-foreground">
                      {run.summary ?? run.error ?? "…"}
                    </span>
                  </span>
                  <span className="shrink-0 text-right">
                    <RunStatusBadge status={run.status} />
                    <span className="block text-[11px] text-muted-foreground">{timeAgo(run.started_at)}</span>
                  </span>
                </Link>
              ))}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Latest alerts</CardTitle>
              <Link href="/alerts/" className="text-xs text-muted-foreground hover:text-foreground">
                View all
              </Link>
            </CardHeader>
            <CardContent className="grid gap-1">
              {alerts.data?.items.length === 0 && (
                <p className="px-2 py-6 text-center text-sm text-muted-foreground">
                  <Bell className="mx-auto mb-2 size-5" />
                  No price changes yet.
                </p>
              )}
              {alerts.data?.items.slice(0, 4).map((alert) => (
                <Link
                  key={alert.id}
                  href={alert.product_id ? `/product/?id=${alert.product_id}` : "/alerts/"}
                  className="min-w-0 rounded-lg px-2 py-2 hover:bg-muted/60"
                >
                  <div className="flex items-start gap-2 text-sm">
                    {!alert.read && <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" />}
                    <span className="flex-1 font-medium">{alert.title}</span>
                    <span className="shrink-0 text-[11px] text-muted-foreground">{timeAgo(alert.created_at)}</span>
                  </div>
                  <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">{alert.message}</p>
                </Link>
              ))}
            </CardContent>
          </Card>
        </div>
      ) : null}
    </>
  );
}
