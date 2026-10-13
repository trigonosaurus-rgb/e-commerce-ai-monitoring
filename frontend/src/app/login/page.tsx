"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { LogIn } from "lucide-react";
import { useRouter } from "next/navigation";

import { LogoMark } from "@/components/logo";
import { useRequestAccess } from "@/components/providers";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, ApiError } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const client = useQueryClient();
  const requestAccess = useRequestAccess();
  const login = useMutation({
    mutationFn: (form: FormData) => api.post("/auth/login", Object.fromEntries(form)),
    onSuccess: async () => {
      await client.resetQueries(); // drop the demo workspace data and load yours
      router.push("/");
    },
    meta: { silent: true },
  });
  const error = login.error instanceof ApiError ? login.error.message : login.error?.message;

  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <Card className="w-full max-w-sm">
        <CardContent className="grid gap-5">
          <div className="flex flex-col items-center gap-2 pt-2 text-center">
            <LogoMark className="size-10" />
            <h1 className="text-xl font-semibold tracking-tight">Sign in to Rivalscope</h1>
            <p className="text-sm text-muted-foreground">Access is by invitation.</p>
          </div>
          <form
            className="grid gap-3"
            onSubmit={(event) => {
              event.preventDefault();
              login.mutate(new FormData(event.currentTarget));
            }}
          >
            <div className="grid gap-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" name="email" type="email" required autoComplete="email" autoFocus />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="password">Password</Label>
              <Input id="password" name="password" type="password" required autoComplete="current-password" />
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" size="lg" disabled={login.isPending}>
              <LogIn /> {login.isPending ? "Signing in…" : "Sign in"}
            </Button>
          </form>
          <p className="border-t pt-4 text-center text-sm text-muted-foreground">
            No account?{" "}
            <button className="font-medium text-foreground underline-offset-4 hover:underline" onClick={() => requestAccess()}>
              Request access
            </button>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
