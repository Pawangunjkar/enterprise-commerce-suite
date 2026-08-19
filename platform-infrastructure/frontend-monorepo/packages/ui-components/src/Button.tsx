import { ButtonHTMLAttributes } from "react";

export function Button({ className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-xl bg-navy px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50 ${className}`}
      {...props}
    />
  );
}
