import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Role Radar | Workday job intelligence",
  description: "Scan your Workday company pipeline for relevant, recently posted roles.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
