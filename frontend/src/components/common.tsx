"use client";

import {
  AlertTriangle,
  ArrowDownRight,
  CheckCircle2,
  CircleDashed,
  Crown,
  Loader2,
  RotateCw,
  Sparkles,
  TrendingUp,
  XCircle,
} from "lucide-react";
import { useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { favicon, pct } from "@/lib/format";
import type { Position, RunStatus, Snapshot } from "@/lib/types";
import { cn } from "@/lib/utils";

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: React.ReactNode;
  description?: React.ReactNode;
  actions?: React.ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div className="min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

const POSITION = {
  cheapest: { label: "Cheapest", icon: Crown, className: "bg-success/12 text-success" },
  competitive: { label: "Competitive", icon: CheckCircle2, className: "bg-primary/10 text-primary" },
  above_market: { label: "Above market", icon: TrendingUp, className: "bg-warning/15 text-warning" },
  no_data: { label: "No data yet", icon: CircleDashed, className: "bg-muted text-muted-foreground" },
} as const;

export function PositionBadge({ position }: { position: Position }) {
  const config = POSITION[position.label];
  const Icon = config.icon;
  const diff = position.diff_vs_lowest_pct;
  return (
    <Badge variant="secondary" className={cn("gap-1 font-medium", config.className)}>
      <Icon />
      {config.label}
      {position.label === "above_market" && diff !== null && (
        <span className="tabular">{pct(diff)}</span>
      )}
    </Badge>
  );
}

const RUN_STATUS: Record<RunStatus, { label: string; icon: typeof Loader2; className: string }> = {
  running: { label: "Running", icon: Loader2, className: "text-primary [&>svg]:animate-spin" },
  completed: { label: "Completed", icon: CheckCircle2, className: "text-success" },
  failed: { label: "Failed", icon: XCircle, className: "text-destructive" },
  interrupted: { label: "Interrupted", icon: AlertTriangle, className: "text-warning" },
};

export function RunStatusBadge({ status }: { status: RunStatus }) {
  const { label, icon: Icon, className } = RUN_STATUS[status];
  return (
    <span className={cn("inline-flex items-center gap-1 text-xs font-medium", className)}>
      <Icon className="size-3.5" /> {label}
    </span>
  );
}

export function StoreIcon({ domain, className = "size-5" }: { domain: string; className?: string }) {
  const [failed, setFailed] = useState(false);
  if (failed) {
    return (
      <span
        className={cn(
          "flex shrink-0 items-center justify-center rounded bg-muted text-[10px] font-semibold uppercase text-muted-foreground",
          className,
        )}
      >
        {domain[0]}
      </span>
    );
  }
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={favicon(domain)}
      alt=""
      className={cn("shrink-0 rounded bg-white object-contain p-px", className)}
      onError={() => setFailed(true)}
      loading="lazy"
    />
  );
}

const METHOD = {
  jsonld: "Structured data",
  microdata: "Structured data",
  meta: "Page meta tags",
  llm: "AI-read · verified",
} as const;

export function MethodBadge({ snapshot }: { snapshot: Pick<Snapshot, "method" | "fetched_via"> }) {
  const ai = snapshot.method === "llm";
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Badge variant="outline" className="gap-1 font-normal text-muted-foreground">
          {ai && <Sparkles className="text-primary" />}
          {METHOD[snapshot.method]}
          {snapshot.fetched_via === "tavily" && <span className="opacity-70">· via Tavily</span>}
        </Badge>
      </TooltipTrigger>
      <TooltipContent className="max-w-64">
        {ai
          ? "The page had no machine-readable price, so the AI read it — and its quote was checked against the page text."
          : "Read from the schema.org data the store publishes for search engines. No AI involved."}
        {snapshot.fetched_via === "tavily" &&
          " The store blocked a direct request, so the page was fetched through Tavily."}
      </TooltipContent>
    </Tooltip>
  );
}

/** A competitor's price relative to yours. Only a cheaper competitor (a threat) is colored. */
export function Delta({ value, className }: { value: number | null; className?: string }) {
  if (value === null || Math.abs(value) < 0.05) return <span className={cn("text-muted-foreground", className)}>—</span>;
  return (
    <span
      title={value < 0 ? "Cheaper than you" : "More expensive than you"}
      className={cn(
        "inline-flex items-center gap-0.5 tabular",
        value < 0 ? "font-medium text-destructive" : "text-muted-foreground",
        className,
      )}
    >
      {value < 0 && <ArrowDownRight className="size-3.5" />}
      {pct(value)}
    </span>
  );
}

export function EmptyState({
  icon: Icon,
  title,
  children,
  action,
}: {
  icon: typeof Sparkles;
  title: string;
  children?: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-dashed px-6 py-12 text-center">
      <span className="mb-3 flex size-11 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Icon className="size-5" />
      </span>
      <h3 className="font-medium">{title}</h3>
      {children && <div className="mt-1 max-w-md text-sm text-muted-foreground">{children}</div>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function QueryError({ error, retry }: { error: Error; retry?: () => void }) {
  return (
    <Alert variant="destructive">
      <AlertTriangle />
      <AlertTitle>Couldn&apos;t load this</AlertTitle>
      <AlertDescription className="flex flex-wrap items-center gap-3">
        <span>{error.message}</span>
        {retry && (
          <Button size="xs" variant="outline" onClick={retry}>
            <RotateCw /> Try again
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}

export function LoadingBlock({ rows = 3 }: { rows?: number }) {
  return (
    <div className="grid gap-3">
      {Array.from({ length: rows }, (_, i) => (
        <Skeleton key={i} className="h-16 w-full rounded-xl" />
      ))}
    </div>
  );
}
