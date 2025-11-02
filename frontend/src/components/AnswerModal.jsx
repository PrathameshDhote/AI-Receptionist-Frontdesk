import React, { useState } from 'react';
import { X, Send, User } from 'lucide-react';

export default function AnswerModal({ request, onClose, onSubmit }) {
  const [answer, setAnswer] = useState('');
  const [supervisorName, setSupervisorName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!answer.trim() || !supervisorName.trim()) {
      alert('Please fill in all fields');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(request.id, answer, supervisorName);
      onClose();
    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800">Answer Customer Question</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Customer Question */}
        <div className="p-6 bg-blue-50 border-b border-blue-100">
          <h3 className="text-sm font-semibold text-blue-800 mb-2">Customer Question:</h3>
          <p className="text-gray-800 text-lg">{request.question}</p>
          <p className="text-sm text-gray-600 mt-2">
            From: {request.caller_info || 'Anonymous'}
          </p>
          <p className="text-xs text-gray-500">
            Asked: {new Date(request.created_at).toLocaleString()}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Supervisor Name */}
          <div>
            <label
              htmlFor="supervisorName"
              className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2"
            >
              <User className="w-4 h-4" />
              <span>Your Name</span>
            </label>
            <input
              type="text"
              id="supervisorName"
              value={supervisorName}
              onChange={(e) => setSupervisorName(e.target.value)}
              placeholder="Enter your name"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Answer */}
          <div>
            <label
              htmlFor="answer"
              className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2"
            >
              <Send className="w-4 h-4" />
              <span>Your Answer</span>
            </label>
            <textarea
              id="answer"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here..."
              rows={6}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              This answer will be sent to the customer and added to the knowledge base.
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full px-6 py-3 font-bold rounded-lg transition-all flex items-center justify-center gap-2 ${isSubmitting
                  ? 'bg-gray-400 text-white opacity-70 cursor-not-allowed'
                  : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl active:scale-95'
                }`}
            >
              <Send className="w-5 h-5" />
              <span>{isSubmitting ? 'Submitting...' : 'Submit Answer'}</span>
            </button>

          </div>
        </form>
      </div>
    </div>
  );
}
