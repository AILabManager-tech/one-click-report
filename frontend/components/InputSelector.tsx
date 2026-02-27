"use client";

interface InputSelectorProps {
  activeTab: "upload" | "paste";
  onTabChange: (tab: "upload" | "paste") => void;
  t: { tab_upload: string; tab_paste: string };
}

export default function InputSelector({ activeTab, onTabChange, t }: InputSelectorProps) {
  return (
    <div className="flex rounded-lg bg-gray-100 p-1">
      {(["upload", "paste"] as const).map((tab) => (
        <button
          key={tab}
          onClick={() => onTabChange(tab)}
          className={`flex-1 rounded-md px-4 py-2.5 text-sm font-medium transition-colors ${
            activeTab === tab
              ? "bg-white text-brand-navy shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          {tab === "upload" ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
              </svg>
              {t.tab_upload}
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9.334a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184" />
              </svg>
              {t.tab_paste}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
