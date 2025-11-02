import React from 'react';
import { BookOpen, Tag, Calendar, TrendingUp } from 'lucide-react';

export default function KnowledgeBaseList({ entries }) {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getSourceBadge = (source) => {
    const colors = {
      initial: 'bg-blue-100 text-blue-800 border-blue-300',
      learned: 'bg-green-100 text-green-800 border-green-300',
      manual: 'bg-purple-100 text-purple-800 border-purple-300',
    };
    return colors[source] || colors.manual;
  };

  if (!entries || entries.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12 text-center">
        <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-600 mb-2">
          No Knowledge Base Entries
        </h3>
        <p className="text-gray-500">
          Knowledge base entries will appear here when supervisors answer questions.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center space-x-2">
          <BookOpen className="w-6 h-6 text-blue-600" />
          <span>Knowledge Base</span>
          <span className="text-sm font-normal text-gray-500">
            ({entries.length} entries)
          </span>
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow border-t-4 border-blue-500"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <span
                className={`px-2 py-1 rounded-full text-xs font-semibold border ${getSourceBadge(
                  entry.source
                )}`}
              >
                {entry.source.toUpperCase()}
              </span>
              {entry.use_count > 0 && (
                <div className="flex items-center space-x-1 text-xs text-gray-500">
                  <TrendingUp className="w-3 h-3" />
                  <span>{entry.use_count} uses</span>
                </div>
              )}
            </div>

            {/* Question */}
            <div className="mb-3">
              <div className="flex items-center space-x-2 mb-2">
                <Tag className="w-4 h-4 text-blue-600" />
                <h3 className="font-semibold text-gray-800 text-sm">Question:</h3>
              </div>
              <p className="text-gray-700 text-sm font-medium">
                {entry.question}
              </p>
            </div>

            {/* Answer */}
            <div className="mb-3">
              <h4 className="text-xs font-semibold text-gray-600 mb-1">Answer:</h4>
              <p className="text-gray-600 text-sm line-clamp-3">
                {entry.answer}
              </p>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100">
              <div className="flex items-center space-x-1">
                <Calendar className="w-3 h-3" />
                <span>{formatDate(entry.created_at)}</span>
              </div>
              <span className="text-xs text-gray-400">
                ID: {entry.id.substring(0, 8)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
