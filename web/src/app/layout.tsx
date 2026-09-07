import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";

import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SME Credit Appraisal",
  description:
    "Dual-objective decision support for SME credit appraisal: credit risk and development impact, scored separately and explainably.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans">
        <header className="border-b border-slate-200 bg-white">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
            <Link href="/" className="flex items-baseline gap-2.5">
              <span className="text-sm font-semibold text-slate-900">
                SME Credit Appraisal
              </span>
              <span className="text-xs text-slate-400">
                decision support &middot; prototype
              </span>
            </Link>
            <nav className="flex items-center gap-4 text-sm">
              <Link href="/" className="text-slate-600 hover:text-slate-900">
                Appraisals
              </Link>
              <Link href="/model" className="text-slate-600 hover:text-slate-900">
                Model
              </Link>
              <Link
                href="/appraisals/new"
                className="rounded-md bg-slate-900 px-3 py-1.5 text-white hover:bg-slate-800"
              >
                New appraisal
              </Link>
            </nav>
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-6">{children}</main>

        <footer className="border-t border-slate-200 bg-white">
          <div className="mx-auto max-w-7xl px-6 py-3 text-xs text-slate-400">
            Research prototype. Criterion weights are not yet elicited — scores
            must not be used for lending decisions or reported as results.
          </div>
        </footer>
      </body>
    </html>
  );
}
