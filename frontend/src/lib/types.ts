// Mirrors backend/api/schemas.py — keep both in sync when the API changes.

export type PositionLabel = "cheapest" | "competitive" | "above_market" | "no_data";

export interface Position {
  own_price: number | null;
  lowest: number | null;
  median: number | null;
  competitors: number;
  diff_vs_lowest_pct: number | null;
  label: PositionLabel;
}

export interface Snapshot {
  id: number;
  price: number;
  currency: string;
  in_stock: boolean | null;
  method: "jsonld" | "microdata" | "meta" | "llm";
  fetched_via: "direct" | "tavily";
  evidence: string;
  flagged: boolean;
  flag_reason: string | null;
  captured_at: string;
  run_id: number | null;
}

export type OfferStatus = "proposed" | "tracking" | "rejected" | "paused";

export interface Offer {
  id: number;
  is_own: boolean;
  store: string;
  domain: string;
  url: string;
  status: OfferStatus;
  source: "agent" | "manual";
  match_confidence: number | null;
  match_reason: string | null;
  title: string | null;
  last_price: number | null;
  currency: string | null;
  in_stock: boolean | null;
  last_checked_at: string | null;
  next_check_at: string | null;
  fail_count: number;
  last_error: string | null;
  needs_review: boolean;
  latest: Snapshot | null;
}

export interface ProductSummary {
  id: number;
  name: string;
  brand: string | null;
  image_url: string | null;
  currency: string | null;
  position: Position;
  lowest_store: string | null;
  tracking: number;
  proposed: number;
  attention: number;
  last_checked_at: string | null;
  trend: { day: string; lowest: number | null; own: number | null }[];
}

export interface Alert {
  id: number;
  product_id: number | null;
  run_id: number | null;
  kind: "price_drop" | "price_increase" | "undercut" | "stock" | "needs_review";
  title: string;
  message: string;
  links: { label: string; url: string }[];
  read: boolean;
  delivered: string[];
  created_at: string;
}

export type RunStatus = "running" | "completed" | "failed" | "interrupted";

export interface Run {
  id: number;
  kind: "discovery" | "check";
  title: string;
  status: RunStatus;
  summary: string | null;
  error: string | null;
  product_id: number | null;
  product_name: string | null;
  tokens_in: number;
  tokens_out: number;
  cost_usd: number;
  started_at: string;
  finished_at: string | null;
}

export interface ProductDetail {
  id: number;
  name: string;
  brand: string | null;
  mpn: string | null;
  gtin: string | null;
  image_url: string | null;
  currency: string | null;
  market: string | null;
  created_at: string;
  position: Position;
  offers: Offer[];
  alerts: Alert[];
  runs: Run[];
}

export interface HistorySeries {
  offer_id: number;
  store: string;
  is_own: boolean;
  currency: string | null;
  points: { t: string; price: number; flagged: boolean; snapshot_id: number }[];
}

export type EventLevel = "info" | "success" | "warning" | "error";

export interface Decision {
  domain: string;
  url: string;
  title: string;
  favicon: string | null;
  verdict: string;
  confidence: number;
  reason: string;
  kept: boolean;
}

export interface MarketStore {
  domain: string;
  source: "search" | "knowledge";
  kind: string;
  kept: boolean;
  reason: string;
}

export interface RunEvent {
  seq: number;
  ts: string;
  step: string;
  level: EventLevel;
  message: string;
  data: {
    url?: string;
    store?: string;
    price?: number;
    currency?: string;
    evidence?: string;
    method?: string;
    via?: string;
    confidence?: number;
    queries?: string[];
    retailers?: string[];
    query?: string | null;
    stores?: MarketStore[];
    market?: string | null;
    decisions?: Decision[];
    results?: { title: string; url: string; domain: string; favicon: string | null }[];
    offers?: { domain: string; url: string; price: number; currency: string; confidence: number }[];
    pages?: { store: string; url: string }[];
    [key: string]: unknown;
  } | null;
}

export interface Dashboard {
  products: number;
  competitors: number;
  proposed: number;
  attention: number;
  alerts_7d: number;
  unread_alerts: number;
  checks_7d: number;
  cost_30d_usd: number;
  positions: Partial<Record<PositionLabel, number>>;
  last_check_at: string | null;
}

export interface Me {
  email: string | null;
  demo: boolean;
}

export interface Meta {
  app_name: string;
  contact_email: string | null;
  contact_telegram: string | null;
  check_interval_hours: number;
  features: { ai: boolean; search: boolean; telegram: boolean; email: boolean };
}

export interface NotificationSettings {
  notify_email: boolean;
  alert_email: string | null;
  notify_telegram: boolean;
  telegram_connected: boolean;
  telegram_available: boolean;
  email_available: boolean;
}
