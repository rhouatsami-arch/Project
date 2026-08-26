import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import { AppProviders } from "@/components/app-providers";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "MatiousHire",
  description: "MatiousHire — student profiles, candidate applications, and recruiter pipelines",
  icons: {
    icon: "/matious-logo.png",
  },
};

const bootScript = `(function(){try{var k="matioushire-theme";var s=localStorage.getItem(k);var d=window.matchMedia("(prefers-color-scheme: dark)").matches;var t=s==="light"||s==="dark"?s:d?"dark":"light";document.documentElement.dataset.theme=t;document.documentElement.style.colorScheme=t;}catch(e){}var keys=["originalPrompt","prompt.js"];function guard(message,source){if(!message&&!source)return false;return keys.some(function(key){return(message&&message.indexOf(key)!==-1)||(source&&source.indexOf(key)!==-1);});}window.addEventListener("error",function(event){if(guard(event.message,event.filename)){event.preventDefault();event.stopImmediatePropagation();return true;}},true);})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={jakarta.variable} suppressHydrationWarning>
      <body>
        <script dangerouslySetInnerHTML={{ __html: bootScript }} />
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
