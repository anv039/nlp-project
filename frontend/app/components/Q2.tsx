"use client";
import { useState } from "react";

export default function Q2() {
  const tabs = [
    { id: 1, label: "Similarity Scores", src: "/similarity_scores.png" },
    { id: 2, label: "Vector Heatmap", src: "/vector_heatmap.png" },
  ];

  const [activeTab, setActiveTab] = useState(tabs[0]);

  return (
    <div className="w-full max-w-3xl mx-auto">
      
      {/* Tabs */}
      <div className="flex gap-2 border-b mb-4 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 whitespace-nowrap border-b-2 transition ${
              activeTab.id === tab.id
                ? "border-blue-500 text-blue-500 font-semibold"
                : "border-transparent text-gray-500 hover:text-black"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Image Display */}
      <div className="w-full h-[400px] flex items-center justify-center border rounded-lg overflow-hidden">
        <img
          src={activeTab.src}
          alt={activeTab.label}
          className="max-h-full object-contain"
        />
      </div>
    </div>
  );
}