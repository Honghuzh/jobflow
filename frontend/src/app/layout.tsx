import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JobFlow — 智能求职助手",
  description: "基于 Agent 的智能求职助手",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className="min-h-screen bg-background text-foreground antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
