import type { ReactNode } from "react";

export function AppShell({
  children,
  eyebrow,
  title,
  description,
  actions,
}: {
  children: ReactNode;
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
}) {
  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#f6f1e7_0%,#f2ede4_100%)]">
      <div className="mx-auto flex max-w-7xl flex-col gap-8 px-6 py-8 lg:px-10">
        <section className="rounded-[2rem] border border-border bg-white/80 p-8 backdrop-blur">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-primary">{eyebrow}</p>
              <h1 className="mt-3 text-4xl font-semibold text-foreground">{title}</h1>
              <p className="mt-3 max-w-3xl text-base leading-7 text-muted-foreground">{description}</p>
            </div>
            {actions ? <div className="flex items-center gap-3">{actions}</div> : null}
          </div>
        </section>
        {children}
      </div>
    </main>
  );
}
