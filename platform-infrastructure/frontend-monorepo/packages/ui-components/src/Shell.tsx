import { PropsWithChildren } from "react";
export function Shell({ title, children }: PropsWithChildren<{ title: string }>) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <h1 className="text-xl font-bold tracking-tight">{title}</h1>
      </header>
      <main className="mx-auto max-w-7xl p-6">{children}</main>
    </div>
  );
}
