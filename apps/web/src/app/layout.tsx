import type { Metadata } from "next";
import { IBM_Plex_Sans, Space_Grotesk } from "next/font/google";

import "./globals.css";

const bodyFont = IBM_Plex_Sans({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

const headingFont = Space_Grotesk({
  variable: "--font-heading",
  subsets: ["latin"],
  weight: ["500", "700"],
});

export const metadata: Metadata = {
  title: {
    default: "研究方法自动分析平台",
    template: "%s | 研究方法自动分析平台",
  },
  description: "面向 MVP 的研究方法浏览前端，提供首页、方法列表页和方法详情页。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className={`${bodyFont.variable} ${headingFont.variable} antialiased`}>{children}</body>
    </html>
  );
}
