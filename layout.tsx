import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "基金定投助手",
  description: "基金定投、滚存、收益率与 XIRR 管理工具",
  manifest: "/manifest.webmanifest",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}