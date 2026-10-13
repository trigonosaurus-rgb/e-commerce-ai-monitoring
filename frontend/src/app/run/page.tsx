"use client";

import {
  ArrowRight,
  BookOpenText,
  Check,
  ChevronDown,
  CircleAlert,
  CircleCheck,
  CircleDot,
  CircleX,
  Clock,
  Coins,
  ExternalLink,
  Info,
  ListChecks,
  Loader2,
  PlayCircle,
  Search,
  ShieldCheck,
  Sparkles,
  Square,
  Wand2,
} from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";

import { LoadingBlock, QueryError, RunStatusBadge, StoreIcon } from "@/components/common";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { clock, duration, money, usd } from "@/lib/format";
import { useRun, useRunEvents } from "@/lib/queries";
import type { Decision, Run, RunEvent } from "@/lib/types";
import { cn } from "@/lib/utils";

const DISCOVERY_STEPS = [
  { key: "read_product", label: "Read your product", icon: BookOpenText },
  { key: "plan_queries", label: "Plan searches", icon: Wand2 },
  { key: "search", label: "Search the web", icon: Search },
  { key: "screen", label: "Screen results", icon: ListChecks },
  { key: "verify", label: "Verify prices", icon: ShieldCheck },
  { key: "propose", label: "Propose matches", icon: Sparkles },
];

type StepState = "pending" | "active" | "done" | "failed";

function stepStates(events: RunEvent[], run: Run, replaying: boolean): Record<string, StepState> {
  const order = DISCOVERY_STEPS.map((s) => s.key);
  const last = [...events].reverse().find((e) => order.includes(e.step));
  const lastIndex = last ? order.indexOf(last.step) : -1;
  const live = run.status === "running" || replaying;
  const failed = !replaying && (run.status === "failed" || run.status === "interrupted");
  const result: Record<string, StepState> = {};
  order.forEach((key, i) => {
    if (i < lastIndex) result[key] = "done";
    else if (i === lastIndex) result[key] = failed ? "failed" : live ? "active" : "done";
    else result[key] = "pending";
  });
  return result;
}

function Pipeline({ events, run, replaying }: { events: RunEvent[]; run: Run; replaying: boolean }) {
  const states = stepStates(events, run, replaying);
  const attempts = events.filter((e) => e.step === "plan_queries" && e.message.startsWith("Searching")).length;
  return (
    <ol className="grid gap-1">
      {DISCOVERY_STEPS.map(({ key, label, icon: Icon }, i) => {
        const state = states[key];
        return (
          <li
            key={key}
            className={cn(
              "flex items-center gap-3 rounded-lg px-2.5 py-2 text-sm transition-colors",
              state === "active" && "bg-primary/8 font-medium text-foreground",
              state === "pending" && "text-muted-foreground",
            )}
          >
            <span
              className={cn(
                "flex size-7 shrink-0 items-center justify-center rounded-full border",
                state === "done" && "border-success/30 bg-success/10 text-success",
                state === "active" && "border-primary/40 bg-primary/10 text-primary",
                state === "failed" && "border-destructive/40 bg-destructive/10 text-destructive",
              )}
            >
              {state === "done" ? (
                <Check className="size-3.5" />
              ) : state === "active" ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : state === "failed" ? (
                <CircleX className="size-3.5" />
              ) : (
                <Icon className="size-3.5" />
              )}
            </span>
            <span className="flex-1">
              <span className="text-muted-foreground tabular">{i + 1}.</span> {label}
            </span>
            {key === "plan_queries" && attempts > 1 && (
              <Badge variant="outline" className="text-[10px]">
                {attempts} attempts
              </Badge>
            )}
          </li>
        );
      })}
    </ol>
  );
}

const LEVEL_ICON = {
  info: { icon: CircleDot, className: "text-muted-foreground" },
  success: { icon: CircleCheck, className: "text-success" },
  warning: { icon: CircleAlert, className: "text-warning" },
  error: { icon: CircleX, className: "text-destructive" },
};

const VERDICT_LABEL: Record<string, string> = {
  same_product: "same product",
  different_product: "other product",
  used_or_refurbished: "used / refurbished",
  other_market: "other market",
  marketplace_or_aggregator: "marketplace / comparison",
  not_a_store_page: "not a store page",
};

function Decisions({ decisions }: { decisions: Decision[] }) {
  const [open, setOpen] = useState(false);
  const kept = decisions.filter((d) => d.kept);
  const dropped = decisions.filter((d) => !d.kept);
  const shown = open ? [...kept, ...dropped] : kept;
  return (
    <div className="mt-2 grid gap-1">
      {shown.map((d, i) => (
        <div key={`${d.url}-${i}`} className={cn("flex items-start gap-2 text-xs", !d.kept && "opacity-70")}>
          <StoreIcon domain={d.domain} className="mt-px size-3.5" />
          <span className="min-w-0 flex-1">
            <a href={d.url} target="_blank" rel="noreferrer" className="font-medium hover:underline">
              {d.domain}
            </a>{" "}
            <span className={d.kept ? "text-success" : "text-muted-foreground"}>
              · {d.kept ? "kept" : VERDICT_LABEL[d.verdict] ?? d.verdict}
            </span>
            <span className="block text-muted-foreground">{d.reason}</span>
          </span>
        </div>
      ))}
      {dropped.length > 0 && (
        <button
          onClick={() => setOpen(!open)}
          className="mt-1 inline-flex w-fit items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
        >
          <ChevronDown className={cn("size-3 transition-transform", open && "rotate-180")} />
          {open ? "Hide" : "Show"} {dropped.length} rejected result{dropped.length === 1 ? "" : "s"} and why
        </button>
      )}
    </div>
  );
}

function EventDetails({ event }: { event: RunEvent }) {
  const d = event.data;
  if (!d) return null;
  return (
    <>
      {(d.queries?.length || d.retailers?.length) && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {d.queries?.map((q) => (
            <Badge key={q} variant="outline" className="h-auto max-w-full font-mono text-[11px] font-normal break-all whitespace-normal">
              <Search /> {q}
            </Badge>
          ))}
          {d.retailers?.map((r) => (
            <Badge key={r} variant="secondary" className="gap-1 text-[11px] font-normal">
              <StoreIcon domain={r} className="size-3" /> {r}
            </Badge>
          ))}
        </div>
      )}
      {d.results && d.results.length > 0 && (
        <div className="mt-2 flex flex-wrap items-center gap-1">
          {d.results.slice(0, 16).map((r) => (
            <a key={r.url} href={r.url} target="_blank" rel="noreferrer" title={`${r.domain} — ${r.title}`}>
              <StoreIcon domain={r.domain} className="size-4" />
            </a>
          ))}
          {d.results.length > 16 && (
            <span className="text-xs text-muted-foreground">+{d.results.length - 16}</span>
          )}
        </div>
      )}
      {d.decisions && <Decisions decisions={d.decisions} />}
      {d.evidence && (
        <pre className="mt-2 max-h-20 max-w-full overflow-auto rounded-md bg-muted/70 px-2 py-1.5 font-mono text-[11px] whitespace-pre-wrap break-all">
          {d.evidence}
        </pre>
      )}
      {d.url && !d.decisions && !d.results && (
        <a
          href={d.url}
          target="_blank"
          rel="noreferrer"
          className="mt-1 inline-flex max-w-full items-center gap-1 truncate text-xs text-muted-foreground hover:text-foreground"
        >
          <ExternalLink className="size-3 shrink-0" /> <span className="truncate">{d.url}</span>
        </a>
      )}
    </>
  );
}

function Feed({ events, live }: { events: RunEvent[]; live: boolean }) {
  return (
    <ol className="relative grid gap-4 before:absolute before:top-2 before:bottom-2 before:left-[9px] before:w-px before:bg-border">
      {events.map((event) => {
        const { icon: Icon, className } = LEVEL_ICON[event.level];
        return (
          <li key={event.seq} className="relative flex animate-rise gap-3">
            <Icon className={cn("relative z-10 mt-0.5 size-[19px] shrink-0 rounded-full bg-card", className)} />
            <div className="min-w-0 flex-1">
              <div className="flex items-baseline justify-between gap-3">
                <p className="min-w-0 text-sm break-words">{event.message}</p>
                <span className="shrink-0 font-mono text-[11px] text-muted-foreground">{clock(event.ts)}</span>
              </div>
              <EventDetails event={event} />
            </div>
          </li>
        );
      })}
      {live && (
        <li className="relative flex items-center gap-3 text-sm text-muted-foreground">
          <Loader2 className="relative z-10 size-[19px] shrink-0 animate-spin rounded-full bg-card text-primary" />
          Working…
        </li>
      )}
    </ol>
  );
}

function Candidates({ events }: { events: RunEvent[] }) {
  const verified = events.filter((e) => e.step === "verify");
  if (!verified.length) return null;
  return (
    <Card>
      <CardHeader>
        <CardTitle>Checked stores</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-2 sm:grid-cols-2">
        {verified.map((e) => {
          const ok = e.level === "success";
          const domain = e.data?.store ?? e.message.split(":")[0];
          const reason =
            (e.data?.reason as string | undefined) ??
            e.message.slice(domain.length + 1).replace(/^ rejected — /, "").replace(/^ [^—]*— /, "");
          return (
            <div
              key={e.seq}
              className={cn(
                "flex animate-rise items-start gap-2.5 rounded-lg border p-3",
                ok ? "border-success/30 bg-success/[0.04]" : "bg-muted/30 opacity-80",
              )}
            >
              <StoreIcon domain={domain} className="mt-0.5 size-5" />
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-sm font-medium">{domain}</span>
                  {ok && e.data?.price !== undefined ? (
                    <span className="text-sm font-semibold tabular">{money(e.data.price, e.data.currency)}</span>
                  ) : (
                    <Badge variant="outline" className="text-[10px]">rejected</Badge>
                  )}
                </div>
                <p className="mt-0.5 text-xs text-muted-foreground">{reason}</p>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}

/** Plays a finished run back at ~8x speed, with pauses capped so it stays watchable. */
function useReplay(events: RunEvent[]) {
  const [shown, setShown] = useState<number | null>(null);
  useEffect(() => {
    if (shown === null) return;
    if (shown >= events.length) {
      const done = setTimeout(() => setShown(null), 1500);
      return () => clearTimeout(done);
    }
    const gap =
      shown === 0 ? 400 : new Date(events[shown].ts).getTime() - new Date(events[shown - 1].ts).getTime();
    const timer = setTimeout(() => setShown(shown + 1), Math.min(Math.max(gap / 8, 250), 1100));
    return () => clearTimeout(timer);
  }, [shown, events]);
  return {
    replaying: shown !== null,
    visible: shown === null ? events : events.slice(0, shown),
    start: () => setShown(0),
    stop: () => setShown(null),
  };
}

function RunView() {
  const id = Number(useSearchParams().get("id")) || null;
  const run = useRun(id);
  const live = run.data?.status === "running";
  const events = useRunEvents(id, live);
  const all = useMemo(() => events.data ?? [], [events.data]);
  const replay = useReplay(all);

  if (run.error) return <QueryError error={run.error} retry={() => run.refetch()} />;
  if (!run.data || !events.data) return <LoadingBlock rows={4} />;
  const r = run.data;
  const discovery = r.kind === "discovery";
  const visible = replay.visible;
  const finished = !live && !replay.replaying;

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="mb-1 flex items-center gap-2 text-xs text-muted-foreground">
            <Link href="/activity/" className="hover:text-foreground">Agent activity</Link>
            <span>/</span>
            <span>Run #{r.id}</span>
          </div>
          <h1 className="text-xl font-semibold tracking-tight md:text-2xl">{r.title}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
            <RunStatusBadge status={r.status} />
            <span className="inline-flex items-center gap-1"><Clock className="size-3.5" /> {duration(r.started_at, r.finished_at)}</span>
            <span className="inline-flex items-center gap-1 tabular">
              <Coins className="size-3.5" /> {usd(r.cost_usd)} · {(r.tokens_in + r.tokens_out).toLocaleString("en")} tokens
            </span>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {!live && all.length > 2 &&
            (replay.replaying ? (
              <Button variant="outline" onClick={replay.stop}><Square /> Stop replay</Button>
            ) : (
              <Button variant="outline" onClick={replay.start}><PlayCircle /> Replay</Button>
            ))}
          {r.product_id && (
            <Button asChild>
              <Link href={`/product/?id=${r.product_id}`}>
                {discovery && finished && r.status === "completed" ? "Review matches" : "Open product"} <ArrowRight />
              </Link>
            </Button>
          )}
        </div>
      </div>

      {finished && (r.summary || r.error) && (
        <div
          className={cn(
            "flex items-start gap-2 rounded-lg border px-4 py-3 text-sm",
            r.status === "completed" ? "border-success/30 bg-success/[0.05]" : "border-destructive/30 bg-destructive/[0.05]",
          )}
        >
          {r.status === "completed" ? <CircleCheck className="mt-0.5 size-4 text-success" /> : <CircleAlert className="mt-0.5 size-4 text-destructive" />}
          <span>{r.error ?? r.summary}</span>
        </div>
      )}

      <div className={cn("grid gap-6", discovery && "lg:grid-cols-[260px_1fr]")}>
        {discovery && (
          <div className="lg:sticky lg:top-6 lg:self-start">
            <Card size="sm">
              <CardContent>
                <Pipeline events={visible} run={r} replaying={replay.replaying} />
              </CardContent>
            </Card>
            <p className="mt-3 flex gap-1.5 px-1 text-xs text-muted-foreground">
              <Info className="mt-0.5 size-3.5 shrink-0" />
              Every decision below is logged with its reason — nothing happens off the record.
            </p>
          </div>
        )}
        <div className="grid min-w-0 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {live || replay.replaying ? (
                  <span className="relative flex size-2">
                    <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-60" />
                    <span className="relative inline-flex size-2 rounded-full bg-primary" />
                  </span>
                ) : null}
                {replay.replaying ? "Replay" : live ? "Live feed" : "Journal"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Feed events={visible} live={live || replay.replaying} />
            </CardContent>
          </Card>
          {discovery && <Candidates events={visible} />}
        </div>
      </div>
    </div>
  );
}

export default function RunPage() {
  return (
    <Suspense fallback={<LoadingBlock rows={4} />}>
      <RunView />
    </Suspense>
  );
}
