"use client";

import { useQuery } from "@tanstack/react-query";
import { ExternalLink, FileSearch, Flag } from "lucide-react";

import { MethodBadge } from "@/components/common";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { api } from "@/lib/api";
import { dateTime, money } from "@/lib/format";
import type { Offer, Snapshot } from "@/lib/types";

function EvidenceText({ text }: { text: string }) {
  return (
    <pre className="max-h-32 overflow-auto rounded-md bg-muted/70 px-2.5 py-2 font-mono text-[11px] leading-relaxed whitespace-pre-wrap break-all">
      {text || "—"}
    </pre>
  );
}

/** Every price is backed by the exact fragment it was read from — this is where users see it. */
export function EvidenceDialog({ offer }: { offer: Offer }) {
  const readings = useQuery({
    queryKey: ["snapshots", offer.id],
    queryFn: () => api.get<Snapshot[]>(`/offers/${offer.id}/snapshots?limit=50`),
    enabled: false,
  });

  return (
    <Dialog onOpenChange={(open) => open && readings.refetch()}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="xs" disabled={!offer.latest}>
          <FileSearch /> Evidence
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Where this price comes from</DialogTitle>
          <DialogDescription className="flex items-center gap-1 break-all">
            <a href={offer.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 hover:text-foreground">
              {offer.url} <ExternalLink className="size-3 shrink-0" />
            </a>
          </DialogDescription>
        </DialogHeader>
        <div className="grid max-h-[60vh] gap-3 overflow-y-auto pr-1">
          {(readings.data ?? (offer.latest ? [offer.latest] : [])).map((snap, i) => (
            <div key={snap.id} className={i === 0 ? "" : "border-t pt-3"}>
              <div className="mb-1.5 flex flex-wrap items-center gap-2 text-sm">
                <span className="font-semibold tabular">{money(snap.price, snap.currency)}</span>
                <span className="text-xs text-muted-foreground">{dateTime(snap.captured_at)}</span>
                <MethodBadge snapshot={snap} />
                {snap.in_stock === false && <span className="text-xs text-destructive">out of stock</span>}
                {snap.flagged && (
                  <span className="inline-flex items-center gap-1 text-xs text-warning">
                    <Flag className="size-3" /> {snap.flag_reason}
                  </span>
                )}
              </div>
              <EvidenceText text={snap.evidence} />
            </div>
          ))}
          {readings.isFetching && <p className="text-xs text-muted-foreground">Loading history…</p>}
        </div>
      </DialogContent>
    </Dialog>
  );
}
