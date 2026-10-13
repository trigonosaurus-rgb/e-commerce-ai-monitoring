"use client";

import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  Bot,
  Check,
  ExternalLink,
  Link2,
  MoreHorizontal,
  Pause,
  Play,
  Plus,
  Radar,
  RefreshCw,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { toast } from "sonner";

import { PriceChart, seriesColors, Swatch } from "@/components/charts";
import {
  Delta,
  EmptyState,
  LoadingBlock,
  MethodBadge,
  PositionBadge,
  QueryError,
  RunStatusBadge,
  StoreIcon,
} from "@/components/common";
import { EvidenceDialog } from "@/components/evidence-dialog";
import { useRequestAccess } from "@/components/providers";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { api } from "@/lib/api";
import { money, timeAgo, usd } from "@/lib/format";
import {
  useHistory,
  useInvalidateWorkspace,
  useMe,
  useProduct,
  useUpdateOffer,
} from "@/lib/queries";
import type { Offer, ProductDetail } from "@/lib/types";
import { cn } from "@/lib/utils";

function Stat({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="mt-1 text-lg font-semibold tracking-tight">{children}</div>
    </div>
  );
}

function ProposedMatches({ product }: { product: ProductDetail }) {
  const proposed = product.offers.filter((o) => o.status === "proposed");
  const update = useUpdateOffer();
  if (!proposed.length) return null;
  return (
    <Card className="border-primary/30 bg-primary/[0.03] ring-primary/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="size-4 text-primary" /> The agent found {proposed.length} matching
          offer{proposed.length === 1 ? "" : "s"}
        </CardTitle>
        <CardDescription>
          Approve the ones that really are the same product — only approved pages are monitored.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3 md:grid-cols-2">
        {proposed.map((offer) => (
          <div key={offer.id} className="flex flex-col gap-3 rounded-lg border bg-card p-3">
            <div className="flex items-start gap-2.5">
              <StoreIcon domain={offer.domain} className="mt-0.5 size-5" />
              <div className="min-w-0 flex-1">
                <a
                  href={offer.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 font-medium hover:underline"
                >
                  {offer.store} <ExternalLink className="size-3 text-muted-foreground" />
                </a>
                <div className="truncate text-xs text-muted-foreground">{offer.title}</div>
              </div>
              <div className="text-right">
                <div className="font-semibold tabular">{money(offer.last_price, offer.currency)}</div>
                <Delta
                  className="text-xs"
                  value={
                    offer.last_price && product.position.own_price
                      ? ((offer.last_price - product.position.own_price) / product.position.own_price) * 100
                      : null
                  }
                />
              </div>
            </div>
            <div className="rounded-md bg-muted/60 px-2.5 py-2 text-xs">
              <div className="mb-1 flex items-center justify-between gap-2">
                <span className="font-medium">Why the agent thinks it matches</span>
                {offer.match_confidence !== null && (
                  <span className="tabular text-muted-foreground">
                    {Math.round(offer.match_confidence * 100)}% sure
                  </span>
                )}
              </div>
              <span className="text-muted-foreground">{offer.match_reason}</span>
            </div>
            <div className="mt-auto flex items-center gap-2">
              <Button
                size="sm"
                onClick={() => update.mutate({ id: offer.id, status: "tracking" })}
                disabled={update.isPending}
              >
                <Check /> Track it
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => update.mutate({ id: offer.id, status: "rejected" })}
                disabled={update.isPending}
              >
                <X /> Not the same
              </Button>
              <span className="ml-auto">
                <EvidenceDialog offer={offer} />
              </span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

function OfferActions({ offer }: { offer: Offer }) {
  const update = useUpdateOffer();
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon-xs" aria-label="More actions">
          <MoreHorizontal />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem asChild>
          <a href={offer.url} target="_blank" rel="noreferrer">
            <ExternalLink /> Open page
          </a>
        </DropdownMenuItem>
        {offer.status === "paused" ? (
          <DropdownMenuItem onClick={() => update.mutate({ id: offer.id, status: "tracking" })}>
            <Play /> Resume checks
          </DropdownMenuItem>
        ) : (
          <DropdownMenuItem onClick={() => update.mutate({ id: offer.id, status: "paused" })}>
            <Pause /> Pause checks
          </DropdownMenuItem>
        )}
        {!offer.is_own && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              variant="destructive"
              onClick={() => update.mutate({ id: offer.id, status: "rejected" })}
            >
              <Trash2 /> Stop tracking
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function ReviewNotice({ offer }: { offer: Offer }) {
  const invalidate = useInvalidateWorkspace();
  const review = useMutation({
    mutationFn: (accept: boolean) => api.post(`/offers/${offer.id}/review`, { accept }),
    onSuccess: invalidate,
  });
  const reading = offer.latest;
  return (
    <div className="mt-1.5 flex flex-wrap items-center gap-2 rounded-md bg-warning/10 px-2 py-1.5 text-xs text-warning">
      <AlertTriangle className="size-3.5" />
      <span>
        New reading {money(reading?.price, reading?.currency)} looks off ({reading?.flag_reason}).
      </span>
      <Button size="xs" variant="outline" onClick={() => review.mutate(true)}>
        Accept
      </Button>
      <Button size="xs" variant="ghost" onClick={() => review.mutate(false)}>
        Dismiss
      </Button>
    </div>
  );
}

function OffersTable({ product }: { product: ProductDetail }) {
  const offers = product.offers.filter((o) => o.status === "tracking" || o.status === "paused");
  const colors = seriesColors(offers);
  const own = product.position.own_price;
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Store</TableHead>
          <TableHead className="text-right">Price</TableHead>
          <TableHead className="text-right">vs you</TableHead>
          <TableHead className="hidden md:table-cell">Stock</TableHead>
          <TableHead className="hidden md:table-cell">Checked</TableHead>
          <TableHead className="hidden lg:table-cell">Read from</TableHead>
          <TableHead />
        </TableRow>
      </TableHeader>
      <TableBody>
        {offers.map((offer) => (
          <TableRow key={offer.id} className={cn(offer.status === "paused" && "opacity-60")}>
            <TableCell className="max-w-72 whitespace-normal">
              <div className="flex items-center gap-2">
                <Swatch color={colors.get(offer.id)} />
                <StoreIcon domain={offer.domain} className="size-4" />
                <a href={offer.url} target="_blank" rel="noreferrer" className="truncate font-medium hover:underline">
                  {offer.store}
                </a>
                {offer.is_own && <Badge variant="secondary">You</Badge>}
                {offer.status === "paused" && <Badge variant="outline">Paused</Badge>}
                {offer.fail_count > 0 && (
                  <Tooltip>
                    <TooltipTrigger>
                      <AlertTriangle className="size-3.5 text-warning" />
                    </TooltipTrigger>
                    <TooltipContent className="max-w-72">
                      Last check failed: {offer.last_error}. Retrying automatically.
                    </TooltipContent>
                  </Tooltip>
                )}
              </div>
              {offer.needs_review && <ReviewNotice offer={offer} />}
            </TableCell>
            <TableCell className="text-right font-medium tabular">
              {money(offer.last_price, offer.currency)}
            </TableCell>
            <TableCell className="text-right">
              {offer.is_own ? (
                <span className="text-muted-foreground">—</span>
              ) : (
                <Delta
                  value={offer.last_price && own ? ((offer.last_price - own) / own) * 100 : null}
                />
              )}
            </TableCell>
            <TableCell className="hidden md:table-cell">
              {offer.in_stock === null ? (
                <span className="text-muted-foreground">—</span>
              ) : offer.in_stock ? (
                <span className="text-success">In stock</span>
              ) : (
                <span className="text-destructive">Out of stock</span>
              )}
            </TableCell>
            <TableCell className="hidden text-muted-foreground md:table-cell">
              {timeAgo(offer.last_checked_at)}
            </TableCell>
            <TableCell className="hidden lg:table-cell">
              {offer.latest && <MethodBadge snapshot={offer.latest} />}
            </TableCell>
            <TableCell className="text-right">
              <span className="inline-flex items-center gap-1">
                <EvidenceDialog offer={offer} />
                <OfferActions offer={offer} />
              </span>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function AddCompetitorDialog({ productId, open, onOpenChange }: {
  productId: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const invalidate = useInvalidateWorkspace();
  const add = useMutation({
    mutationFn: (url: string) => api.post<Offer>(`/products/${productId}/offers`, { url }),
    onSuccess: async (offer) => {
      toast.success(`Tracking ${offer.store}. The first price will appear in a moment.`);
      onOpenChange(false);
      await invalidate();
    },
  });
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add a competitor page</DialogTitle>
          <DialogDescription>
            Know a store selling this product? Paste the product page — it is checked right away.
          </DialogDescription>
        </DialogHeader>
        <form
          className="grid gap-3"
          onSubmit={(event) => {
            event.preventDefault();
            add.mutate(String(new FormData(event.currentTarget).get("url")));
          }}
        >
          <Input name="url" placeholder="https://store.example/product" required autoFocus />
          <DialogFooter>
            <Button type="submit" disabled={add.isPending}>
              <Link2 /> {add.isPending ? "Adding…" : "Track this page"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function ProductActions({ product }: { product: ProductDetail }) {
  const router = useRouter();
  const { data: me } = useMe();
  const requestAccess = useRequestAccess();
  const invalidate = useInvalidateWorkspace();
  const [adding, setAdding] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const busy = product.runs.some((r) => r.status === "running");

  const startRun = useMutation({
    mutationFn: (kind: "check" | "discover") =>
      api.post<{ run_id: number }>(`/products/${product.id}/${kind}`),
    onSuccess: ({ run_id }, kind) => {
      invalidate();
      if (kind === "discover") router.push(`/run/?id=${run_id}`);
      else toast.success("Checking prices now…", {
        action: { label: "Watch", onClick: () => router.push(`/run/?id=${run_id}`) },
      });
    },
  });
  const remove = useMutation({
    mutationFn: () => api.delete(`/products/${product.id}`),
    onSuccess: async () => {
      await invalidate();
      router.push("/");
    },
  });
  const guard = (action: () => void) => () => (me?.demo ? requestAccess() : action());

  return (
    <>
      <Button variant="outline" onClick={guard(() => startRun.mutate("check"))} disabled={busy || startRun.isPending}>
        <RefreshCw className={cn(busy && "animate-spin")} /> Check now
      </Button>
      <Button onClick={guard(() => startRun.mutate("discover"))} disabled={busy || startRun.isPending}>
        <Bot /> Find competitors
      </Button>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" aria-label="More">
            <MoreHorizontal />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={guard(() => setAdding(true))}>
            <Plus /> Add competitor link
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem variant="destructive" onClick={guard(() => setDeleting(true))}>
            <Trash2 /> Delete product
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <AddCompetitorDialog productId={product.id} open={adding} onOpenChange={setAdding} />
      <Dialog open={deleting} onOpenChange={setDeleting}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete “{product.name}”?</DialogTitle>
            <DialogDescription>
              Its price history and alerts are deleted too. Agent runs stay in the activity log.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDeleting(false)}>Cancel</Button>
            <Button variant="destructive" onClick={() => remove.mutate()} disabled={remove.isPending}>
              <Trash2 /> Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

function ProductView() {
  const id = Number(useSearchParams().get("id")) || null;
  const product = useProduct(id);
  const history = useHistory(id);

  if (product.error) return <QueryError error={product.error} retry={() => product.refetch()} />;
  if (!product.data) return <LoadingBlock rows={4} />;
  const p = product.data;
  const own = p.offers.find((o) => o.is_own);
  const tracked = p.offers.filter((o) => !o.is_own && o.status === "tracking");

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex min-w-0 items-center gap-4">
          <div className="flex size-16 shrink-0 items-center justify-center overflow-hidden rounded-xl border bg-white">
            {p.image_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={p.image_url} alt="" className="size-full object-contain" />
            ) : (
              <Radar className="size-6 text-muted-foreground" />
            )}
          </div>
          <div className="min-w-0">
            <h1 className="text-xl font-semibold tracking-tight md:text-2xl">{p.name}</h1>
            <div className="mt-1 flex flex-wrap gap-x-3 text-xs text-muted-foreground">
              {p.brand && <span>{p.brand}</span>}
              {p.gtin && <span className="tabular">EAN {p.gtin}</span>}
              {p.market && <span className="capitalize">{p.market} market</span>}
              {own && (
                <a href={own.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 hover:text-foreground">
                  your page <ExternalLink className="size-3" />
                </a>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <ProductActions product={p} />
        </div>
      </div>

      <Card>
        <CardContent className="grid grid-cols-2 gap-5 md:grid-cols-4">
          <Stat label="Your price">{money(p.position.own_price, p.currency)}</Stat>
          <Stat label="Cheapest competitor">{money(p.position.lowest, p.currency)}</Stat>
          <Stat label="Market median">{money(p.position.median, p.currency)}</Stat>
          <Stat label="Your position">
            <PositionBadge position={p.position} />
          </Stat>
        </CardContent>
      </Card>

      <ProposedMatches product={p} />

      {tracked.length === 0 && !p.offers.some((o) => o.status === "proposed") ? (
        <EmptyState icon={Bot} title="No competitors tracked yet">
          Let the agent search for stores selling this product, or add a competitor link yourself.
        </EmptyState>
      ) : (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Price history</CardTitle>
              <CardDescription>Readings flagged for review are not drawn until you accept them.</CardDescription>
            </CardHeader>
            <CardContent>
              {history.data ? <PriceChart series={history.data} currency={p.currency} /> : <LoadingBlock rows={1} />}
            </CardContent>
          </Card>
          <Card className="gap-0 pb-0">
            <CardHeader className="pb-3">
              <CardTitle>Tracked pages</CardTitle>
              <CardDescription>Every price links to the exact page fragment it was read from.</CardDescription>
            </CardHeader>
            <OffersTable product={p} />
          </Card>
        </>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Alerts</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {p.alerts.length === 0 && <p className="text-sm text-muted-foreground">No alerts for this product yet.</p>}
            {p.alerts.map((alert) => (
              <div key={alert.id} className="text-sm">
                <div className="flex items-start justify-between gap-2">
                  <span className="font-medium">{alert.title}</span>
                  <span className="shrink-0 text-xs text-muted-foreground">{timeAgo(alert.created_at)}</span>
                </div>
                <p className="mt-0.5 text-xs text-muted-foreground">{alert.message}</p>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Agent runs</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-1">
            {p.runs.map((run) => (
              <Link key={run.id} href={`/run/?id=${run.id}`} className="flex min-w-0 items-center gap-3 rounded-lg px-2 py-1.5 text-sm hover:bg-muted/60">
                <span className="min-w-0 flex-1 truncate">{run.summary ?? run.title}</span>
                <span className="text-xs text-muted-foreground tabular">{usd(run.cost_usd)}</span>
                <RunStatusBadge status={run.status} />
                <span className="w-20 text-right text-xs text-muted-foreground">{timeAgo(run.started_at)}</span>
              </Link>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function ProductPage() {
  return (
    <Suspense fallback={<LoadingBlock rows={4} />}>
      <ProductView />
    </Suspense>
  );
}
