"use client";

import { useEffect, useRef } from "react";

type AdFormat = "auto" | "fluid" | "rectangle" | "horizontal" | "vertical";

interface AdUnitProps {
  slot: string;
  format?: AdFormat;
  responsive?: boolean;
  className?: string;
}

declare global {
  interface Window {
    adsbygoogle: unknown[];
  }
}

export default function AdUnit({
  slot,
  format = "auto",
  responsive = true,
  className = "",
}: AdUnitProps) {
  const adRef = useRef<HTMLModElement>(null);
  const pushed = useRef(false);
  const adClient = process.env.NEXT_PUBLIC_ADSENSE_ID;

  useEffect(() => {
    if (!adClient || pushed.current) return;

    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
      pushed.current = true;
    } catch {
      // AdSense not loaded yet or ad blocker active
    }
  }, [adClient]);

  if (!adClient) {
    // TODO(human): Decide what to render when AdSense is not configured (dev/preview mode).
    // Options: return null (hide), or return a visible placeholder for layout testing.
    // If placeholder: consider showing format type, slot name, and approximate dimensions
    // so you can verify ad positioning before going live.
    return null;
  }

  return (
    <div className={`ad-container overflow-hidden text-center ${className}`}>
      <ins
        ref={adRef}
        className="adsbygoogle"
        style={{ display: "block" }}
        data-ad-client={adClient}
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive={responsive ? "true" : "false"}
      />
    </div>
  );
}
