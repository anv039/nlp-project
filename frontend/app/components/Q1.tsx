"use client";
import { useState, useEffect } from "react";
import Papa from "papaparse";

export default function Q1() {
  const tabs = [
    { id: 1, label: "Class Distribution", src: "/class_distribution.png", type: "img" },
    { id: 2, label: "Confusion Matrices", src: "/confusion_matrices.png", type: "img" },
    { id: 3, label: "Model Comparison", src: "/model_comparison.png", type: "img" },
    { id: 4, label: "NB Validation Curve", src: "/nb_validation_curve.png", type: "img" },
    { id: 5, label: "SVM Validation Curve", src: "/svm_validation_curve.png", type: "img" },
    { id: 6, label: "Results Table", src: "/results.csv", type: "csv" },
  ];

  const [activeTab, setActiveTab] = useState(tabs[0]);
  const [csvData, setCsvData] = useState([]);

  useEffect(() => {
    if (activeTab.type === "csv") {
      Papa.parse(activeTab.src, {
        download: true,
        header: true,
        complete: (result) => {
          setCsvData(result.data);
        },
      });
    }
  }, [activeTab]);

  return (
    <div className="w-full max-w-6xl mx-auto px-4">
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
            {tab.label || "CSV"}
          </button>
        ))}
      </div>

      {/* Conditional Render */}
      {activeTab.type === "img" ? (
        <div className="w-full h-[400px] flex items-center justify-center border rounded-lg overflow-hidden">
          <img
            src={activeTab.src}
            alt={activeTab.label}
            className="max-h-full object-contain"
          />
        </div>
      ) : (
        <div className="overflow-x-auto border rounded-lg max-h-[500px] text-black">
          <table className="min-w-full text-sm border-collapse">
            <thead className="bg-gray-100 sticky top-0">
              <tr>
                {csvData[0] &&
                  Object.keys(csvData[0]).map((key) => (
                    <th key={key} className="px-4 py-2 border">
                      {key}
                    </th>
                  ))}
              </tr>
            </thead>
            <tbody>
              {csvData.map((row, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  {Object.values(row).map((val, j) => (
                    <td key={j} className="px-4 py-2 border">
                      {val}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}