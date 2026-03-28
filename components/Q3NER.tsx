'use client';

import { useState, useTransition } from 'react';
import { analyzeNER, type NERResult, type CSVResult } from '../actions';

export default function Q3NER() {
  const [activeMode, setActiveMode] = useState<'text' | 'csv'>('text');
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<NERResult | null>(null);
  const [csvResults, setCsvResults] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [isPending, startTransition] = useTransition();

  const getEntityColor = (type: string) => {
    switch(type) {
      case 'PERSON': return 'bg-red-100 text-red-800 border-red-200';
      case 'ORGANIZATION': return 'bg-green-100 text-green-800 border-green-200';
      case 'LOCATION': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleTextAnalysis = (formData: FormData) => {
    setError('');
    setResult(null);
    setCsvResults([]);
    startTransition(async () => {
      const response = await analyzeNER(formData);
      if (response.success) {
        setResult(response.data as NERResult);
      } else {
        setError(response.error);
      }
    });
  };

  const handleCSVAnalysis = (formData: FormData) => {
    setError('');
    setCsvResults([]);
    setResult(null);
    startTransition(async () => {
      const response = await analyzeNER(formData);
      if (response.success) {
        setCsvResults((response.data as CSVResult).results);
      } else {
        setError(response.error);
      }
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex space-x-4 border-b border-gray-200 pb-4">
        <button
          onClick={() => setActiveMode('text')}
          className={`py-2 px-4 ${activeMode === 'text' ? 'text-blue-600 border-b-2 border-blue-600 font-medium' : 'text-gray-500'}`}
        >
          Single Text Input
        </button>
        <button
          onClick={() => setActiveMode('csv')}
          className={`py-2 px-4 ${activeMode === 'csv' ? 'text-blue-600 border-b-2 border-blue-600 font-medium' : 'text-gray-500'}`}
        >
          CSV Upload
        </button>
      </div>

      {activeMode === 'text' && (
        <form action={handleTextAnalysis} className="space-y-4 text-black">
          <input type="hidden" name="mode" value="text" />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter text for NER analysis:
            </label>
            <textarea
              name="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="Example: STORA ENSO, NORSKE SKOG, M-REAL, UPM-KYMMENE Credit Suisse First Boston..."
              disabled={isPending}
            />
          </div>
          <button
            type="submit"
            disabled={isPending || !text.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isPending ? 'Processing NER...' : 'Analyze Text'}
          </button>
        </form>
      )}

      {activeMode === 'csv' && (
        <form action={handleCSVAnalysis} className="space-y-4 text-black">
          <input type="hidden" name="mode" value="csv" />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload CSV file with 'text' column:
            </label>
            <input
              type="file"
              name="file"
              accept=".csv"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              disabled={isPending}
            />
            <p className="text-sm text-gray-500 mt-1">
              CSV should contain a 'text' column
            </p>
          </div>
          <button
            type="submit"
            disabled={isPending || !file}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isPending ? 'Processing CSV...' : 'Upload & Analyze'}
          </button>
        </form>
      )}

      {error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          Error: {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6 p-6 bg-white border rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900">NER Results:</h3>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-700 mb-2">Text:</h4>
            <p className="text-gray-600 whitespace-pre-wrap">{result.text}</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
{Object.entries(result?.entities ?? {}).map(([type, entities]) => (
              <div key={type} className="border p-4 rounded-lg">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-semibold text-gray-900 capitalize">{type}</h4>
                  <span className="text-sm font-bold text-blue-600">{result.counts[type as keyof typeof result.counts]}</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {[...new Set(entities.slice(0, 20))].map((entity, idx) => (
                    <span key={idx} className={`px-2 py-1 text-sm rounded-full border text-black`}>
                      {entity}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {csvResults.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            CSV Results ({csvResults.length} rows):
          </h3>
          <div className="overflow-x-auto border rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Text Preview</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">PERSON</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ORG</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">LOC</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {csvResults.map((row, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 text-sm text-gray-900 max-w-md truncate">{row.text}</td>
                    <td className="px-6 py-4 text-sm font-medium text-red-600">{row.counts.PERSON}</td>
                    <td className="px-6 py-4 text-sm font-medium text-green-600">{row.counts.ORGANIZATION}</td>
                    <td className="px-6 py-4 text-sm font-medium text-blue-600">{row.counts.LOCATION}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
