'use client';

import { useState } from 'react';
import Q3NER from './components/Q3NER';
import Q4Chatbot from './components/Q4Chatbot';
import Q1 from './components/Q1';
import Q2 from './components/Q2';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'q1' | 'q2' | 'q3' | 'q4'>('q3');

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            NLP Project
          </h1>
          <p className="text-gray-600 mt-2">
            Stock Market Financial News Sentiment Analysis
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('q1')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === 'q1'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
              `}
            >
             Q1: Sentiment
            </button>
            <button
              onClick={() => setActiveTab('q2')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === 'q2'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
              `}
            >
             Q2: Embeddings
            </button>
            <button
              onClick={() => setActiveTab('q3')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === 'q3'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
              `}
            >
             Q3: Named Entity Recognition
            </button>
            <button
              onClick={() => setActiveTab('q4')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === 'q4'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
              `}
            >
              Q4: NLP Chatbot
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="mt-8">
          {activeTab === 'q1' && <Q1 />}
          {activeTab === 'q2' && <Q2 />}
          {activeTab === 'q3' && <Q3NER />}
          {activeTab === 'q4' && <Q4Chatbot />}
        </div>
      </div>
    </div>
  );
}