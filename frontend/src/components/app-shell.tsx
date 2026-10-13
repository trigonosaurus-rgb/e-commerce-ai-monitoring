"use client";

import { useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  Bell,
  LayoutDashboard,
  LogIn,
  LogOut,
  Menu,
  Monitor,
  Moon,
  Plus,
  Settings,
  Sun,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { useState, useSyncExternalStore } from "react";

import { Logo } from "@/components/logo";
import { useRequestAccess } from "@/components/providers";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { api } from "@/lib/api";
import { useAlerts, useMe } from "@/lib/queries";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/activity/", label: "Agent activity", icon: Activity },
  { href: "/alerts/", label: "Alerts", icon: Bell },
  { href: "/settings/", label: "Settings", icon: Settings },
];

function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/" || pathname.startsWith("/product");
  if (href === "/activity/") return pathname.startsWith("/activity") || pathname.startsWith("/run");
  return pathname.startsWith(href.replace(/\/$/, ""));
}

/** "Add product" — opens the access dialog in the demo instead of a dead end. */
export function AddProductButton({ className }: { className?: string }) {
  const { data: me } = useMe();
  const requestAccess = useRequestAccess();
  if (me?.demo) {
    return (
      <Button className={className} onClick={() => requestAccess()}>
        <Plus /> Add product
      </Button>
    );
  }
  return (
    <Button asChild className={className}>
      <Link href="/add/">
        <Plus /> Add product
      </Link>
    </Button>
  );
}

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const { data: alerts } = useAlerts();
  return (
    <nav className="grid gap-0.5">
      {NAV.map(({ href, label, icon: Icon }) => (
        <Link
          key={href}
          href={href}
          onClick={onNavigate}
          className={cn(
            "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground",
            isActive(pathname, href) && "bg-muted font-medium text-foreground",
          )}
        >
          <Icon className="size-4" />
          <span className="flex-1">{label}</span>
          {href === "/alerts/" && !!alerts?.unread && (
            <span className="rounded-full bg-primary px-1.5 text-[11px] font-medium text-primary-foreground tabular-nums">
              {alerts.unread}
            </span>
          )}
        </Link>
      ))}
    </nav>
  );
}

// true only in the browser: the theme is unknown while rendering on the server
const useIsClient = () =>
  useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );

function ThemeToggle() {
  const { theme: chosen, setTheme } = useTheme();
  const theme = useIsClient() ? chosen : undefined;
  const options = [
    { value: "light", icon: Sun },
    { value: "dark", icon: Moon },
    { value: "system", icon: Monitor },
  ];
  return (
    <div className="flex rounded-lg bg-muted p-0.5" role="radiogroup" aria-label="Theme">
      {options.map(({ value, icon: Icon }) => (
        <button
          key={value}
          role="radio"
          aria-checked={theme === value}
          aria-label={value}
          onClick={() => setTheme(value)}
          className={cn(
            "flex flex-1 items-center justify-center rounded-md py-1 text-muted-foreground transition-colors",
            theme === value && "bg-background text-foreground shadow-sm",
          )}
        >
          <Icon className="size-3.5" />
        </button>
      ))}
    </div>
  );
}

function Account() {
  const { data: me } = useMe();
  const client = useQueryClient();
  const router = useRouter();
  if (!me || me.demo) {
    return (
      <Button variant="outline" size="sm" asChild className="w-full">
        <Link href="/login/">
          <LogIn /> Sign in
        </Link>
      </Button>
    );
  }
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm hover:bg-muted">
          <span className="flex size-7 items-center justify-center rounded-full bg-primary/15 text-xs font-semibold uppercase text-primary">
            {me.email?.[0]}
          </span>
          <span className="min-w-0 flex-1 truncate">{me.email}</span>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-56">
        <DropdownMenuLabel className="truncate">{me.email}</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/settings/">
            <Settings /> Settings
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={async () => {
            await api.post("/auth/logout");
            await client.resetQueries();
            router.push("/");
          }}
        >
          <LogOut /> Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function DemoBanner() {
  const { data: me } = useMe();
  const requestAccess = useRequestAccess();
  if (!me?.demo) return null;
  return (
    <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 border-b bg-primary/[0.06] px-4 py-2 text-center text-sm">
      <span>
        <span className="font-medium">Live demo workspace</span>
        <span className="text-muted-foreground"> · real data, read-only</span>
      </span>
      <span className="flex items-center gap-2">
        <Button size="xs" onClick={() => requestAccess()}>
          Request access
        </Button>
        <Button size="xs" variant="ghost" asChild>
          <Link href="/login/">Sign in</Link>
        </Button>
      </span>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const sidebar = (onNavigate?: () => void) => (
    <div className="flex h-full flex-col gap-6 p-4">
      <Link href="/" onClick={onNavigate} className="px-1.5">
        <Logo />
      </Link>
      <AddProductButton className="w-full" />
      <NavLinks onNavigate={onNavigate} />
      <div className="mt-auto grid gap-3">
        <ThemeToggle />
        <Account />
      </div>
    </div>
  );

  return (
    <div className="flex min-h-screen flex-col">
      <div className="flex flex-1">
        <aside className="sticky top-0 hidden h-screen w-60 shrink-0 border-r bg-sidebar md:block">
          {sidebar()}
        </aside>
        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-30 flex items-center justify-between border-b bg-background/80 px-4 py-2.5 backdrop-blur md:hidden">
            <Link href="/">
              <Logo />
            </Link>
            <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Open menu">
                  <Menu />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-64 p-0">
                <SheetTitle className="sr-only">Navigation</SheetTitle>
                {sidebar(() => setMenuOpen(false))}
              </SheetContent>
            </Sheet>
          </header>
          <DemoBanner />
          <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 md:px-8 md:py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
