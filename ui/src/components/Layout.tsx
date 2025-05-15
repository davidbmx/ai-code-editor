import React from "react";
import { Separator } from "@/components/ui/separator";

interface LayoutProps {
  chatPanel: React.ReactNode;
  previewPanel: React.ReactNode;
}

export function Layout({ chatPanel, previewPanel }: LayoutProps) {
  return (
    <div className="grid grid-cols-[1fr_2fr] h-dvh w-full overflow-hidden">
      {/* Left panel - Chat */}
      <div className="border-r border-border h-full">{chatPanel}</div>

      {/* Right panel - Preview */}
      <div className="h-full">{previewPanel}</div>
    </div>
  );
}
