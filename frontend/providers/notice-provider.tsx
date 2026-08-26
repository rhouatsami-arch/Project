"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";

type NoticeContextValue = {
  notice: string;
  showNotice: (message: string) => void;
};

const NoticeContext = createContext<NoticeContextValue | null>(null);

export function NoticeProvider({ children }: { children: React.ReactNode }) {
  const [notice, setNotice] = useState("");

  const showNotice = useCallback((message: string) => {
    setNotice(message);
    window.setTimeout(() => setNotice(""), 4000);
  }, []);

  const value = useMemo(() => ({ notice, showNotice }), [notice, showNotice]);

  return (
    <NoticeContext.Provider value={value}>
      {notice && <div className="notice">{notice}</div>}
      {children}
    </NoticeContext.Provider>
  );
}

export function useNotice() {
  const context = useContext(NoticeContext);
  if (!context) throw new Error("useNotice must be used within NoticeProvider");
  return context;
}
