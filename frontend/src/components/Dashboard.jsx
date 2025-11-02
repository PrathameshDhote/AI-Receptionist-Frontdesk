import React, { useState, useEffect } from 'react';
import { RefreshCw, Bell, BellOff, Wifi, WifiOff, AlertCircle, CheckCircle2 } from 'lucide-react';
import { apiService } from '../services/api';
import websocketService from '../services/websocket';
import Stats from './Stats';
import HelpRequestCard from './HelpRequestCard';
import KnowledgeBaseList from './KnowledgeBaseList';
import AnswerModal from './AnswerModal';


export default function Dashboard() {
  const [helpRequests, setHelpRequests] = useState([]);
  const [knowledgeBase, setKnowledgeBase] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [activeTab, setActiveTab] = useState('requests');
  const [debugInfo, setDebugInfo] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);


  // Load initial data
  useEffect(() => {
    loadData();

    websocketService.connect();
    const unsubscribe = websocketService.subscribe(handleWebSocketMessage);

    return () => {
      unsubscribe();
      websocketService.disconnect();
    };
  }, []);


  const loadData = async () => {
    setIsLoading(true);
    try {
      console.log('📋 Loading data...');

      const [requestsData, kbData, statsData] = await Promise.all([
        apiService.getHelpRequests(),
        apiService.getKnowledgeBase(),
        apiService.getStats(),
      ]);

      console.log('✅ All requests:', requestsData);
      console.log('✅ All KB entries:', kbData);
      console.log('✅ Stats:', statsData);

      setHelpRequests(requestsData);
      setKnowledgeBase(kbData);
      setStats(statsData);
      setLastUpdated(new Date());

      // DEBUG INFO
      const debugText = `
Total Requests: ${requestsData.length}
Pending: ${requestsData.filter(r => r.status === 'pending').length}
Resolved: ${requestsData.filter(r => r.status === 'resolved').length}
Timeout: ${requestsData.filter(r => r.status === 'timeout').length}`;
      setDebugInfo(debugText);

    } catch (error) {
      console.error('❌ Error loading data:', error);
      setDebugInfo(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };


  const handleWebSocketMessage = (data) => {
    console.log('📨 WebSocket message:', data);

    if (data.type === 'connection') {
      setWsConnected(data.status === 'connected');
      return;
    }

    if (notifications && Notification.permission === 'granted') {
      new Notification('Frontdesk AI Update', {
        body: getNotificationMessage(data),
        icon: '/vite.svg',
      });
    }

    if (['new_request', 'request_resolved', 'knowledge_base_updated'].includes(data.type)) {
      console.log('🔄 Reloading data...');
      loadData();
    }
  };


  const getNotificationMessage = (data) => {
    switch (data.type) {
      case 'new_request':
        return `New help request: ${data.data?.question}`;
      case 'request_resolved':
        return `Request resolved by ${data.data?.answered_by}`;
      case 'knowledge_base_updated':
        return 'Knowledge base updated';
      default:
        return 'New update';
    }
  };


  const handleAnswerSubmit = async (requestId, answer, supervisorName) => {
    try {
      await apiService.answerHelpRequest(requestId, answer, supervisorName);
      await loadData();
      setSelectedRequest(null);
    } catch (error) {
      console.error('❌ Error submitting answer:', error);
      throw error;
    }
  };


  const toggleNotifications = () => {
    if (!notifications && Notification.permission === 'default') {
      Notification.requestPermission().then((permission) => {
        if (permission === 'granted') {
          setNotifications(true);
        }
      });
    } else {
      setNotifications(!notifications);
    }
  };


  // Get requests by status
  const pendingRequests = helpRequests.filter((r) => r.status === 'pending');
  const resolvedRequests = helpRequests.filter((r) => r.status === 'resolved');


  return (
    <div className="min-h-screen bg-gray-50">
      {/* IMPROVED HEADER */}
      <header className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {/* Title and Status Row */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-gray-900">
                Frontdesk AI
              </h1>
              <p className="text-md text-gray-600 mt-1">
                Human-in-the-Loop AI Receptionist System
              </p>
            </div>

            {/* Status Indicators */}
            <div className="flex items-center space-x-8">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                {wsConnected ? (
                  <>
                    <div className="flex items-center space-x-2 px-3 py-2 bg-green-50 rounded-lg border border-green-200">
                      <Wifi className="w-5 h-5 text-green-600" />
                      <span className="text-sm font-medium text-green-700">Connected</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex items-center space-x-2 px-3 py-2 bg-red-50 rounded-lg border border-red-200">
                      <WifiOff className="w-5 h-5 text-red-600" />
                      <span className="text-sm font-medium text-red-700">Disconnected</span>
                    </div>
                  </>
                )}
              </div>

              {/* Notifications Toggle */}
              <button
                onClick={toggleNotifications}
                title={notifications ? 'Notifications On' : 'Notifications Off'}
                className={`p-3 rounded-lg transition-all transform hover:scale-110 ${notifications
                    ? 'bg-blue-100 text-blue-600 border border-blue-300'
                    : 'bg-gray-100 text-gray-600 border border-gray-300'
                  }`}
              >
                {notifications ? (
                  <Bell className="w-6 h-6" />
                ) : (
                  <BellOff className="w-6 h-6" />
                )}
              </button>
            </div>
          </div>

          {/* HIGHLIGHTED REFRESH BUTTON ROW */}
          <div className="flex items-center justify-between bg-gradient-to-r from-blue-50 to-blue-100 border-2 border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              {lastUpdated && (
                <div className="text-sm text-gray-700">
                  <span className="font-semibold">Last updated:</span> {lastUpdated.toLocaleTimeString()}
                </div>
              )}
            </div>

            {/* BIG REFRESH BUTTON - FIXED: DARKER BACKGROUND */}
            <button
              onClick={loadData}
              disabled={isLoading}
              className={`flex items-center gap-2 px-6 py-2 rounded-lg font-bold whitespace-nowrap transition-all flex-shrink-0 ${isLoading
                  ? 'bg-blue-500 text-white opacity-75 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-700 to-blue-800 text-white hover:from-blue-800 hover:to-blue-900 shadow-lg hover:shadow-xl active:scale-95'
                }`}
            >
              <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
              <span className="text-sm">{isLoading ? 'Refreshing...' : 'Refresh Data'}</span>
            </button>
          </div>

          {/* DEBUG INFO */}
          {debugInfo && (
            <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded text-sm text-yellow-800 font-mono">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                <pre className="whitespace-pre-wrap break-words">{debugInfo}</pre>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <Stats stats={stats} />

        {/* Tabs */}
        <div className="mb-8 bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('requests')}
                className={`py-4 px-1 border-b-2 font-semibold text-sm transition-colors ${activeTab === 'requests'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                  }`}
              >
                <span className="flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>Help Requests ({helpRequests.length} total, {pendingRequests.length} pending)</span>
                </span>
              </button>
              <button
                onClick={() => setActiveTab('knowledge')}
                className={`py-4 px-1 border-b-2 font-semibold text-sm transition-colors ${activeTab === 'knowledge'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                  }`}
              >
                <span className="flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Knowledge Base ({knowledgeBase.length} entries)</span>
                </span>
              </button>
            </nav>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'requests' ? (
          <div className="space-y-8">
            {/* Pending Requests */}
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
                <span>⏳ Pending Requests</span>
                <span className="text-blue-600">({pendingRequests.length})</span>
              </h2>
              {pendingRequests.length === 0 ? (
                <div className="bg-white rounded-lg shadow-md p-12 text-center border-2 border-dashed border-gray-300">
                  <CheckCircle2 className="w-12 h-12 text-green-500 mx-auto mb-3" />
                  <p className="text-gray-600 text-lg">No pending requests</p>
                  {helpRequests.length > 0 && (
                    <p className="text-sm text-gray-500 mt-2">
                      All {helpRequests.length} requests have been resolved or timed out
                    </p>
                  )}
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {pendingRequests.map((request) => (
                    <HelpRequestCard
                      key={request.id}
                      request={request}
                      onAnswer={setSelectedRequest}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* All Requests */}
            {helpRequests.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
                  <span>📋 All Requests</span>
                  <span className="text-blue-600">({helpRequests.length})</span>
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {helpRequests.map((request) => (
                    <HelpRequestCard
                      key={request.id}
                      request={request}
                      onAnswer={setSelectedRequest}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Resolved Requests */}
            {resolvedRequests.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
                  <span>✅ Recently Resolved</span>
                  <span className="text-green-600">({resolvedRequests.length})</span>
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {resolvedRequests.slice(0, 6).map((request) => (
                    <HelpRequestCard
                      key={request.id}
                      request={request}
                      onAnswer={setSelectedRequest}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <KnowledgeBaseList entries={knowledgeBase} />
        )}
      </main>

      {/* Answer Modal */}
      {selectedRequest && (
        <AnswerModal
          request={selectedRequest}
          onClose={() => setSelectedRequest(null)}
          onSubmit={handleAnswerSubmit}
        />
      )}
    </div>
  );
}
