"use client";

// Data hooks (TanStack Query). Components never call fetch directly: they use these hooks,
// which cache responses, refetch in the background and poll while an agent run is live.

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "./api";
import type {
  Alert,
  Dashboard,
  HistorySeries,
  Me,
  Meta,
  NotificationSettings,
  Offer,
  ProductDetail,
  ProductSummary,
  Run,
  RunEvent,
} from "./types";

const LIVE_MS = 1500;

export const useMe = () => useQuery({ queryKey: ["me"], queryFn: () => api.get<Me>("/auth/me") });

export const useMeta = () =>
  useQuery({ queryKey: ["meta"], queryFn: () => api.get<Meta>("/meta"), staleTime: Infinity });

export const useDashboard = () =>
  useQuery({ queryKey: ["dashboard"], queryFn: () => api.get<Dashboard>("/dashboard") });

export const useProducts = () =>
  useQuery({ queryKey: ["products"], queryFn: () => api.get<ProductSummary[]>("/products") });

export const useProduct = (id: number | null) =>
  useQuery({
    queryKey: ["product", id],
    queryFn: () => api.get<ProductDetail>(`/products/${id}`),
    enabled: id !== null,
    // keep polling while one of the product's runs is still working
    refetchInterval: (q) => (q.state.data?.runs.some((r) => r.status === "running") ? LIVE_MS : false),
  });

export const useHistory = (id: number | null) =>
  useQuery({
    queryKey: ["history", id],
    queryFn: () => api.get<HistorySeries[]>(`/products/${id}/history`),
    enabled: id !== null,
  });

export const useRuns = (params: { productId?: number; kind?: string } = {}) => {
  const search = new URLSearchParams();
  if (params.productId) search.set("product_id", String(params.productId));
  if (params.kind) search.set("kind", params.kind);
  return useQuery({
    queryKey: ["runs", params],
    queryFn: () => api.get<Run[]>(`/runs?${search}`),
    refetchInterval: (q) => (q.state.data?.some((r) => r.status === "running") ? LIVE_MS : false),
  });
};

export const useRun = (id: number | null) =>
  useQuery({
    queryKey: ["run", id],
    queryFn: () => api.get<Run>(`/runs/${id}`),
    enabled: id !== null,
    refetchInterval: (q) => (q.state.data?.status === "running" ? LIVE_MS : false),
  });

export const useRunEvents = (id: number | null, live: boolean) =>
  useQuery({
    queryKey: ["run-events", id],
    queryFn: () => api.get<RunEvent[]>(`/runs/${id}/events`),
    enabled: id !== null,
    refetchInterval: live ? LIVE_MS : false,
  });

export const useAlerts = () =>
  useQuery({
    queryKey: ["alerts"],
    queryFn: () => api.get<{ items: Alert[]; unread: number }>("/alerts"),
    refetchInterval: 60_000,
  });

export const useNotificationSettings = (enabled: boolean) =>
  useQuery({
    queryKey: ["notifications"],
    queryFn: () => api.get<NotificationSettings>("/settings/notifications"),
    enabled,
  });

/** Mutations that change products/offers refresh everything that shows them. */
export function useInvalidateWorkspace() {
  const client = useQueryClient();
  return () =>
    Promise.all(
      ["products", "product", "history", "dashboard", "runs", "alerts"].map((key) =>
        client.invalidateQueries({ queryKey: [key] }),
      ),
    );
}

export function useUpdateOffer() {
  const invalidate = useInvalidateWorkspace();
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: "tracking" | "rejected" | "paused" }) =>
      api.patch<Offer>(`/offers/${id}`, { status }),
    onSuccess: invalidate,
  });
}
