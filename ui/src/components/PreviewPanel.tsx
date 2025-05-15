import React from "react";

interface PreviewPanelProps {
  url: string;
}

export function PreviewPanel({ url }: PreviewPanelProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-border">
        <h2 className="text-xl font-semibold">Preview</h2>
      </div>
      <div className="flex-1 p-4">
        <iframe
          src={url}
          className="w-full h-full border-none rounded-lg shadow-md bg-white"
          title="Code Preview"
        />
      </div>
    </div>
  );
}
