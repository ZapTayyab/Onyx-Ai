import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatScore(score: number): string {
  return `${(score * 100).toFixed(1)}%`;
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getScoreColor(score: number): string {
  if (score >= 0.8) return "text-emerald-600";
  if (score >= 0.5) return "text-amber-600";
  return "text-red-600";
}

export function getScoreBgColor(score: number): string {
  if (score >= 0.8) return "bg-emerald-100 text-emerald-800";
  if (score >= 0.5) return "bg-amber-100 text-amber-800";
  return "bg-red-100 text-red-800";
}
