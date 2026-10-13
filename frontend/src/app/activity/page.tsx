"use client";

import { Bot, Radar } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { EmptyState, LoadingBlock, PageHeader, QueryError, RunStatusBadge } from "@/components/common";
import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { dateTime, duration, usd } from "@/lib/format";
import { useRuns } from "@/lib/queries";

export default function ActivityPage() {
  const [kind, setKind] = useState<string>("all");
  const runs = useRuns(kind === "all" ? {} : { kind });

  return (
    <>
      <PageHeader
        title="Agent activity"
        description="Every search and price check, with what it did, what it decided and what it cost."
        actions={
          <Tabs value={kind} onValueChange={setKind}>
            <TabsList>
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="discovery">Discovery</TabsTrigger>
              <TabsTrigger value="check">Price checks</TabsTrigger>
            </TabsList>
          </Tabs>
        }
      />
      {runs.error ? (
        <QueryError error={runs.error} retry={() => runs.refetch()} />
      ) : !runs.data ? (
        <LoadingBlock />
      ) : runs.data.length === 0 ? (
        <EmptyState icon={Bot} title="Nothing here yet">
          Agent runs appear here as soon as a product is added or checked.
        </EmptyState>
      ) : (
        <Card className="gap-0 py-0">
          <div className="divide-y">
            {runs.data.map((run) => (
              <Link
                key={run.id}
                href={`/run/?id=${run.id}`}
                className="grid grid-cols-[auto_1fr_auto] items-center gap-x-3 gap-y-1 px-4 py-3 text-sm hover:bg-muted/50 md:grid-cols-[auto_1fr_110px_90px_80px_110px]"
              >
                {run.kind === "discovery" ? (
                  <Bot className="size-4 text-primary" />
                ) : (
                  <Radar className="size-4 text-muted-foreground" />
                )}
                <span className="min-w-0">
                  <span className="block truncate font-medium">{run.title}</span>
                  <span className="block truncate text-xs text-muted-foreground">
                    {run.error ?? run.summary ?? "In progress…"}
                  </span>
                </span>
                <RunStatusBadge status={run.status} />
                <span className="hidden text-xs text-muted-foreground tabular md:block">
                  {duration(run.started_at, run.finished_at)}
                </span>
                <span className="hidden text-xs text-muted-foreground tabular md:block">{usd(run.cost_usd)}</span>
                <span className="hidden text-right text-xs text-muted-foreground md:block">
                  {dateTime(run.started_at)}
                </span>
              </Link>
            ))}
          </div>
        </Card>
      )}
    </>
  );
}
