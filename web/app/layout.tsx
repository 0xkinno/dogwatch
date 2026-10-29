import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { Nav } from "../components/Nav";
import { Footer } from "../components/Footer";

const general = localFont({ src: "../public/fonts/GeneralSans-Semibold.woff2", weight: "600", variable: "--font-general", display: "swap" });
const satoshi = localFont({
  src: [
    { path: "../public/fonts/Satoshi-Regular.woff2", weight: "400" },
    { path: "../public/fonts/Satoshi-Medium.woff2", weight: "500" },
  ],
  variable: "--font-satoshi",
  display: "swap",
});
const instrument = localFont({ src: "../public/fonts/InstrumentSerif-Italic.woff2", weight: "400", style: "italic", variable: "--font-instrument", display: "swap" });
const jetbrains = localFont({
  src: [
    { path: "../public/fonts/JetBrainsMono-Regular.woff2", weight: "400" },
    { path: "../public/fonts/JetBrainsMono-SemiBold.woff2", weight: "600" },
  ],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Dogwatch: your papers keep watch while you do",
  description:
    "An always-on, private assistant that keeps a seafarer's certificates under his control and has every renewal ready before a lapse costs him a contract.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#EEEBE5" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${general.variable} ${satoshi.variable} ${instrument.variable} ${jetbrains.variable}`}>
      <body>
        <a href="#main" className="sr-only">Skip to content</a>
        <Nav />
        <main id="main">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
