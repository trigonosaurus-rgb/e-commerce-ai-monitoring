"use client";

import { useMutation } from "@tanstack/react-query";
import { ArrowRight, BookOpenText, ListChecks, Search, ShieldCheck, Sparkles, Store, Wand2 } from "lucide-react";
import { useRouter } from "next/navigation";

import { PageHeader } from "@/components/common";
import { useRequestAccess } from "@/components/providers";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useInvalidateWorkspace, useMe, useMeta } from "@/lib/queries";

const STEPS = [
  { icon: BookOpenText, text: "Reads your page: product name, brand, EAN and your price" },
  { icon: Wand2, text: "Plans searches for your market and language" },
  { icon: Store, text: "Researches which stores sell this kind of product right now" },
  { icon: Search, text: "Searches the web and collects candidate stores" },
  { icon: ListChecks, text: "Screens out reviews, marketplaces, other markets and other models" },
  { icon: ShieldCheck, text: "Opens each candidate, reads its price and confirms it's the same product" },
  { icon: Sparkles, text: "Proposes matches with its reasoning — you approve what gets tracked" },
];

export default function AddProductPage() {
  const router = useRouter();
  const { data: me } = useMe();
  const { data: meta } = useMeta();
  const requestAccess = useRequestAccess();
  const invalidate = useInvalidateWorkspace();
  const start = useMutation({
    mutationFn: (url: string) => api.post<{ run_id: number }>("/products", { url }),
    onSuccess: ({ run_id }) => {
      invalidate();
      router.push(`/run/?id=${run_id}`);
    },
  });
  const unavailable = meta && !(meta.features.ai && meta.features.search);

  return (
    <div className="mx-auto max-w-2xl">
      <PageHeader
        title="Add a product"
        description="Paste the link to a product page in your store. The agent takes it from there."
      />
      <Card>
        <CardContent>
          <form
            className="flex flex-col gap-2 sm:flex-row"
            onSubmit={(event) => {
              event.preventDefault();
              if (me?.demo) return requestAccess();
              start.mutate(String(new FormData(event.currentTarget).get("url")));
            }}
          >
            <Input
              name="url"
              type="text"
              inputMode="url"
              required
              autoFocus
              placeholder="https://your-store.com/products/…"
              className="h-10 flex-1"
            />
            <Button type="submit" size="lg" className="h-10" disabled={start.isPending || !!unavailable}>
              {start.isPending ? "Starting…" : "Find competitors"} <ArrowRight />
            </Button>
          </form>
          {unavailable && (
            <p className="mt-2 text-xs text-destructive">
              The agent is not configured on this server (missing OpenAI or Tavily key).
            </p>
          )}
          <ol className="mt-6 grid gap-3">
            {STEPS.map(({ icon: Icon, text }, i) => (
              <li key={text} className="flex items-center gap-3 text-sm">
                <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
                  <Icon className="size-3.5" />
                </span>
                <span>
                  <span className="text-muted-foreground tabular">{i + 1}.</span> {text}
                </span>
              </li>
            ))}
          </ol>
          <p className="mt-6 border-t pt-4 text-xs text-muted-foreground">
            Usually takes 30–60 seconds and costs well under a cent in AI usage. You can watch every
            step live.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
