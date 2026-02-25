import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "One-Click Report AI",
  description: "Transform raw data into visual PDF reports with AI summary",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
