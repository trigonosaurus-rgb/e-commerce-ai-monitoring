"use client";

import { useMutation } from "@tanstack/react-query";
import { CheckCircle2, Mail, Send } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import { useMeta } from "@/lib/queries";

export function RequestAccessDialog({
  open,
  onOpenChange,
  reason,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  reason?: string;
}) {
  const { data: meta } = useMeta();
  const send = useMutation({
    mutationFn: (form: FormData) => api.post("/access-requests", Object.fromEntries(form)),
  });

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        onOpenChange(next);
        if (!next) send.reset();
      }}
    >
      <DialogContent className="sm:max-w-md">
        {send.isSuccess ? (
          <div className="flex flex-col items-center gap-3 py-6 text-center">
            <CheckCircle2 className="size-10 text-emerald-500" />
            <DialogTitle>Thanks — request received</DialogTitle>
            <DialogDescription>
              I&apos;ll get back to you shortly with access details and pricing.
            </DialogDescription>
          </div>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle>Monitor your own products</DialogTitle>
              <DialogDescription>
                {reason ??
                  "You're exploring a read-only demo. Rivalscope is available by invitation — tell me about your store and I'll set up your workspace."}
              </DialogDescription>
            </DialogHeader>
            <form
              className="grid gap-3"
              onSubmit={(event) => {
                event.preventDefault();
                send.mutate(new FormData(event.currentTarget));
              }}
            >
              <div className="grid gap-1.5">
                <Label htmlFor="ra-name">Name</Label>
                <Input id="ra-name" name="name" required maxLength={120} autoComplete="name" />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="ra-email">Work email</Label>
                <Input id="ra-email" name="email" type="email" required autoComplete="email" />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="ra-company">Store website</Label>
                <Input id="ra-company" name="company" placeholder="https://" maxLength={200} />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="ra-message">What would you like to monitor?</Label>
                <Textarea id="ra-message" name="message" rows={3} maxLength={2000} />
              </div>
              {/* honeypot: hidden from people, irresistible for bots */}
              <input name="website" tabIndex={-1} autoComplete="off" className="hidden" aria-hidden />
              <Button type="submit" disabled={send.isPending} className="mt-1">
                <Send /> {send.isPending ? "Sending…" : "Request access"}
              </Button>
            </form>
            {(meta?.contact_email || meta?.contact_telegram) && (
              <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 border-t pt-3 text-xs text-muted-foreground">
                <span>or reach me directly:</span>
                {meta.contact_telegram && (
                  <a
                    className="inline-flex items-center gap-1 hover:text-foreground"
                    href={`https://t.me/${meta.contact_telegram}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <Send className="size-3" /> @{meta.contact_telegram}
                  </a>
                )}
                {meta.contact_email && (
                  <a
                    className="inline-flex items-center gap-1 hover:text-foreground"
                    href={`mailto:${meta.contact_email}`}
                  >
                    <Mail className="size-3" /> {meta.contact_email}
                  </a>
                )}
              </div>
            )}
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
