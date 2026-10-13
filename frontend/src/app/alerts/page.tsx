"use client";

import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Bell,
  CheckCheck,
  Mail,
  PackageX,
  Send,
  Swords,
} from "lucide-react";
import Link from "next/link";

import { EmptyState, LoadingBlock, PageHeader, QueryError, StoreIcon } from "@/components/common";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";
import { dateTime } from "@/lib/format";
import { useAlerts, useInvalidateWorkspace, useMe } from "@/lib/queries";
import type { Alert } from "@/lib/types";
import { cn } from "@/lib/utils";

const KIND: Record<Alert["kind"], { label: string; icon: typeof Bell; className: string }> = {
  undercut: { label: "Undercut", icon: Swords, className: "bg-destructive/10 text-destructive" },
  price_drop: { label: "Price drop", icon: ArrowDownRight, className: "bg-warning/12 text-warning" },
  price_increase: { label: "Price increase", icon: ArrowUpRight, className: "bg-success/12 text-success" },
  stock: { label: "Stock change", icon: PackageX, className: "bg-primary/10 text-primary" },
  needs_review: { label: "Needs review", icon: AlertTriangle, className: "bg-warning/12 text-warning" },
};

function DeliveredBadges({ delivered }: { delivered: string[] }) {
  return delivered.map((channel) => {
    const failed = channel.endsWith("_failed");
    const name = channel.replace("_failed", "");
    const Icon = name === "telegram" ? Send : Mail;
    return (
      <Badge key={channel} variant="outline" className={cn("gap-1 text-[10px] font-normal", failed && "text-destructive")}>
        <Icon /> {failed ? `${name} failed` : `sent to ${name}`}
      </Badge>
    );
  });
}

export default function AlertsPage() {
  const alerts = useAlerts();
  const { data: me } = useMe();
  const invalidate = useInvalidateWorkspace();
  const readAll = useMutation({ mutationFn: () => api.post("/alerts/read-all"), onSuccess: invalidate });
  const readOne = useMutation({
    mutationFn: (id: number) => api.post(`/alerts/${id}/read`),
    onSuccess: invalidate,
  });

  return (
    <>
      <PageHeader
        title="Alerts"
        description="Price and stock changes worth your attention. Small moves are recorded but don't alert."
        actions={
          !me?.demo && !!alerts.data?.unread && (
            <Button variant="outline" onClick={() => readAll.mutate()}>
              <CheckCheck /> Mark all read
            </Button>
          )
        }
      />
      {alerts.error ? (
        <QueryError error={alerts.error} retry={() => alerts.refetch()} />
      ) : !alerts.data ? (
        <LoadingBlock />
      ) : alerts.data.items.length === 0 ? (
        <EmptyState icon={Bell} title="No alerts yet">
          When a competitor changes price or stock, you&apos;ll see it here — and in Telegram or
          email if you turn that on in Settings.
        </EmptyState>
      ) : (
        <div className="grid gap-3">
          {alerts.data.items.map((alert) => {
            const kind = KIND[alert.kind];
            const Icon = kind.icon;
            return (
              <Card key={alert.id} size="sm" className={cn(!alert.read && "ring-primary/30")}>
                <CardContent className="flex gap-3">
                  <span className={cn("flex size-9 shrink-0 items-center justify-center rounded-lg", kind.className)}>
                    <Icon className="size-4" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-baseline justify-between gap-x-3">
                      <h3 className="font-medium">
                        {!alert.read && <span className="mr-2 inline-block size-2 rounded-full bg-primary" />}
                        {alert.title}
                      </h3>
                      <span className="text-xs text-muted-foreground">{dateTime(alert.created_at)}</span>
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">{alert.message}</p>
                    <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                      <Badge variant="secondary" className={cn("text-[10px]", kind.className)}>{kind.label}</Badge>
                      {alert.links.map((link) => (
                        <a key={link.url} href={link.url} target="_blank" rel="noreferrer">
                          <Badge variant="outline" className="gap-1 font-normal hover:bg-muted">
                            <StoreIcon domain={link.label} className="size-3" /> {link.label}
                          </Badge>
                        </a>
                      ))}
                      <DeliveredBadges delivered={alert.delivered} />
                      <span className="ml-auto flex gap-1">
                        {alert.product_id && (
                          <Button variant="ghost" size="xs" asChild>
                            <Link href={`/product/?id=${alert.product_id}`}>Open product</Link>
                          </Button>
                        )}
                        {alert.run_id && (
                          <Button variant="ghost" size="xs" asChild>
                            <Link href={`/run/?id=${alert.run_id}`}>See the check</Link>
                          </Button>
                        )}
                        {!alert.read && !me?.demo && (
                          <Button variant="ghost" size="xs" onClick={() => readOne.mutate(alert.id)}>
                            Mark read
                          </Button>
                        )}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </>
  );
}
