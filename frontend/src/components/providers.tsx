"use client";

import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { createContext, useCallback, useContext, useState } from "react";
import { toast } from "sonner";

import { RequestAccessDialog } from "@/components/request-access-dialog";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ApiError } from "@/lib/api";

const RequestAccessContext = createContext<(reason?: string) => void>(() => {});

/** Opens the "Request access" dialog — used by every action that the demo can't do. */
export const useRequestAccess = () => useContext(RequestAccessContext);

export function Providers({ children }: { children: React.ReactNode }) {
  const [accessOpen, setAccessOpen] = useState(false);
  const [accessReason, setAccessReason] = useState<string | undefined>();
  const openAccess = useCallback((reason?: string) => {
    setAccessReason(reason);
    setAccessOpen(true);
  }, []);

  // One error policy for the whole app: demo writes open the access dialog,
  // everything else shows a toast with the server's (already user-friendly) message.
  const [client] = useState(() => {
    const onError = (error: Error) => {
      if (error instanceof ApiError && error.code === "demo_read_only") openAccess();
      else toast.error(error.message);
    };
    return new QueryClient({
      queryCache: new QueryCache({
        onError: (error, query) => {
          if (query.state.data === undefined) return; // first load: the page shows the error
          toast.error(error.message);
        },
      }),
      mutationCache: new MutationCache({
        // forms that show their own inline error opt out with `meta: { silent: true }`
        onError: (error, _vars, _ctx, mutation) => mutation.meta?.silent || onError(error),
      }),
      defaultOptions: {
        queries: {
          staleTime: 10_000,
          retry: (count, error) =>
            !(error instanceof ApiError && error.status >= 400 && error.status < 500) && count < 2,
        },
      },
    });
  });

  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <QueryClientProvider client={client}>
        <TooltipProvider delayDuration={200}>
          <RequestAccessContext.Provider value={openAccess}>
            {children}
            <RequestAccessDialog open={accessOpen} onOpenChange={setAccessOpen} reason={accessReason} />
          </RequestAccessContext.Provider>
          <Toaster richColors closeButton />
        </TooltipProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
