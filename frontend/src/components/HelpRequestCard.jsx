import React from 'react';
import { Clock, User, MessageSquare, Calendar } from 'lucide-react';

export default function HelpRequestCard({ request, onAnswer }) {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'resolved':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'timeout':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow border-l-4 border-blue-500">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-5 h-5 text-blue-600" />
          <span className="text-xs font-medium text-gray-500">
            ID: {request.id.substring(0, 8)}...
          </span>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(
            request.status
          )}`}
        >
          {request.status.toUpperCase()}
        </span>
      </div>

      {/* Question */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Question:</h3>
        <p className="text-gray-700 bg-gray-50 p-3 rounded-md">
          {request.question}
        </p>
      </div>

      {/* Customer Info */}
      <div className="flex items-center space-x-4 mb-4 text-sm text-gray-600">
        <div className="flex items-center space-x-1">
          <User className="w-4 h-4" />
          <span>{request.caller_info || 'Anonymous'}</span>
        </div>
        <div className="flex items-center space-x-1">
          <Calendar className="w-4 h-4" />
          <span>{formatDate(request.created_at)}</span>
        </div>
      </div>

      {/* Timeout Warning */}
      {request.status === 'pending' && (
        <div className="flex items-center space-x-2 mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded">
          <Clock className="w-4 h-4 text-yellow-600" />
          <span className="text-sm text-yellow-700">
            Timeout: {formatDate(request.timeout_at)}
          </span>
        </div>
      )}

      {/* Answer Section */}
      {request.answer ? (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <h4 className="text-sm font-semibold text-green-800 mb-2">
            Answer by {request.answered_by}:
          </h4>
          <p className="text-gray-700">{request.answer}</p>
          <p className="text-xs text-gray-500 mt-2">
            Resolved: {formatDate(request.resolved_at)}
          </p>
        </div>
      ) : (
        <button
          onClick={() => onAnswer(request)}
          className="w-full mt-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold py-2.5 px-4 rounded-lg shadow-md hover:shadow-xl transition-all active:scale-95 flex items-center justify-center gap-2"
        >
          <MessageSquare className="w-5 h-5" />
          <span>Answer Question</span>
        </button>

      )}
    </div>
  );
}
