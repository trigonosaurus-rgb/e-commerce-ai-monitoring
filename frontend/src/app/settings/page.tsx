"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, CircleSlash, LogIn, Mail, Send, Server, Unlink } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { EmptyState, LoadingBlock, PageHeader } from "@/components/common";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { api } from "@/lib/api";
import { timeAgo } from "@/lib/format";
import { useMe, useNotificationSettings } from "@/lib/queries";
import type { NotificationSettings } from "@/lib/types";

interface Health {
  status: string;
  database: string;
  scheduler: { status: string; last_tick: string | null; running_checks: number };
  telegram: { configured: boolean; poller: string; last_error: string | null };
  ai: boolean;
  search: boolean;
  email: boolean;
  models: { fast: string; smart: string };
}

function Notifications({ settings }: { settings: NotificationSettings }) {
  const client = useQueryClient();
  const [email, setEmail] = useState(settings.alert_email ?? "");
  // the Save button only appears while the address differs from the saved one
  const emailChanged = email.trim() !== (settings.alert_email ?? "");
  const save = useMutation({
    mutationFn: (patch: Partial<NotificationSettings>) =>
      api.put<NotificationSettings>("/settings/notifications", {
        notify_email: settings.notify_email,
        alert_email: email.trim() || null,
        notify_telegram: settings.notify_telegram,
        ...patch,
      }),
    onSuccess: (data) => client.setQueryData(["notifications"], data),
  });
  const link = useMutation({
    mutationFn: () => api.post<{ url: string }>("/settings/telegram/link"),
    onSuccess: ({ url }) => {
      window.open(url, "_blank", "noopener");
      toast.info("Press Start in Telegram, then come back — this page updates by itself.");
      const poll = setInterval(() => client.invalidateQueries({ queryKey: ["notifications"] }), 2000);
      setTimeout(() => clearInterval(poll), 60_000);
    },
  });
  const unlink = useMutation({
    mutationFn: () => api.post<NotificationSettings>("/settings/telegram/unlink"),
    onSuccess: (data) => client.setQueryData(["notifications"], data),
  });
  const test = useMutation({
    mutationFn: () => api.post<{ results: Record<string, string> }>("/settings/notifications/test"),
    onSuccess: ({ results }) =>
      Object.entries(results).forEach(([channel, result]) =>
        result === "sent" ? toast.success(`Test sent to ${channel}`) : toast.error(`${channel}: ${result}`),
      ),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Where to send alerts</CardTitle>
        <CardDescription>Alerts always appear in the app. Add channels to get them where you are.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-5">
        <div className="grid gap-3 rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <Send className="size-4 text-sky-500" />
            <div className="flex-1">
              <div className="font-medium">Telegram</div>
              <div className="text-xs text-muted-foreground">
                {settings.telegram_connected ? "Connected to your chat." : "Instant messages from our bot."}
              </div>
            </div>
            {settings.telegram_connected && (
              <Switch
                checked={settings.notify_telegram}
                onCheckedChange={(value) => save.mutate({ notify_telegram: value })}
                aria-label="Telegram alerts"
              />
            )}
          </div>
          {!settings.telegram_available ? (
            <p className="text-xs text-muted-foreground">Telegram is not set up on this server yet.</p>
          ) : settings.telegram_connected ? (
            <Button variant="ghost" size="sm" className="w-fit" onClick={() => unlink.mutate()}>
              <Unlink /> Disconnect
            </Button>
          ) : (
            <Button size="sm" className="w-fit" onClick={() => link.mutate()} disabled={link.isPending}>
              <Send /> Connect Telegram
            </Button>
          )}
        </div>

        <div className="grid gap-3 rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <Mail className="size-4 text-primary" />
            <div className="flex-1">
              <div className="font-medium">Email</div>
              <div className="text-xs text-muted-foreground">A short email per alert.</div>
            </div>
            <Switch
              checked={settings.notify_email}
              disabled={!settings.email_available}
              onCheckedChange={(value) => save.mutate({ notify_email: value })}
              aria-label="Email alerts"
            />
          </div>
          {settings.email_available ? (
            <form
              className="flex gap-2"
              onSubmit={(event) => {
                event.preventDefault();
                if (emailChanged) save.mutate({}, { onSuccess: () => toast.success("Alert email saved") });
              }}
            >
              <Label htmlFor="alert-email" className="sr-only">Alert email</Label>
              <Input id="alert-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              {emailChanged && (
                <Button type="submit" size="sm" className="h-8" disabled={save.isPending}>
                  Save
                </Button>
              )}
            </form>
          ) : (
            <p className="text-xs text-muted-foreground">Email delivery is not set up on this server yet.</p>
          )}
        </div>

        <Button
          variant="outline"
          className="w-fit"
          onClick={() => test.mutate()}
          disabled={test.isPending || !(settings.notify_email || settings.notify_telegram)}
        >
          Send a test alert
        </Button>
      </CardContent>
    </Card>
  );
}

function SystemStatus() {
  const health = useQuery({ queryKey: ["health"], queryFn: () => api.get<Health>("/health"), refetchInterval: 30_000 });
  const h = health.data;
  if (!h) return null;
  const rows: [string, boolean, string][] = [
    ["Database", h.database === "ok", h.database],
    ["Price-check scheduler", h.scheduler.status === "running", `last tick ${timeAgo(h.scheduler.last_tick)}`],
    ["AI models", h.ai, `${h.models.fast} · ${h.models.smart}`],
    ["Web search (Tavily)", h.search, h.search ? "configured" : "not configured"],
    ["Telegram bot", h.telegram.configured && h.telegram.poller !== "error", h.telegram.last_error ?? h.telegram.poller],
    ["Email (SMTP)", h.email, h.email ? "configured" : "not configured"],
  ];
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Server className="size-4" /> System status</CardTitle>
        <CardDescription>What the server can do right now.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-2 text-sm">
        {rows.map(([label, ok, detail]) => (
          <div key={label} className="flex items-center gap-2">
            {ok ? <CheckCircle2 className="size-4 text-success" /> : <CircleSlash className="size-4 text-muted-foreground" />}
            <span className="flex-1">{label}</span>
            <span className="truncate text-xs text-muted-foreground">{detail}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

export default function SettingsPage() {
  const { data: me } = useMe();
  const signedIn = !!me && !me.demo;
  const settings = useNotificationSettings(signedIn);

  return (
    <>
      <PageHeader title="Settings" description={signedIn ? me.email : undefined} />
      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        {!me ? (
          <LoadingBlock rows={2} />
        ) : !signedIn ? (
          <EmptyState
            icon={LogIn}
            title="Sign in to manage alerts"
            action={<Button asChild><Link href="/login/">Sign in</Link></Button>}
          >
            Notification channels belong to your own workspace.
          </EmptyState>
        ) : settings.data ? (
          <Notifications settings={settings.data} />
        ) : (
          <LoadingBlock rows={2} />
        )}
        <div className="grid content-start gap-6">
          <SystemStatus />
          {signedIn && (
            <p className="px-1 text-xs text-muted-foreground">
              Prices are checked automatically every few hours. Each check is listed in{" "}
              <Link href="/activity/" className="underline">Agent activity</Link>. <Badge variant="outline">invite-only</Badge>
            </p>
          )}
        </div>
      </div>
    </>
  );
}
