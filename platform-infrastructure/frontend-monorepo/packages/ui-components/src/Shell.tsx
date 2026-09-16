import { PropsWithChildren, ReactNode } from "react";
export function Shell({ title, children, actions }: PropsWithChildren<{ title: string; actions?: ReactNode }>) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="flex items-center justify-between border-b bg-white px-6 py-4">
        <h1 className="text-xl font-bold tracking-tight">{title}</h1>
        {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
      </header>
      <main className="mx-auto max-w-7xl p-6">{children}</main>
    </div>
  );
}
