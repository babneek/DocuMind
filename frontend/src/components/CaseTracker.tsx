import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Calendar, Clock, AlertCircle, CheckCircle,
  Loader, Scale, ChevronDown, ChevronUp, ExternalLink,
  CalendarDays, CalendarRange, History, Info, RefreshCw
} from 'lucide-react';
import {
  searchByCNR,
  searchByCaseNumber,
  getUpcomingHearings,
  type CaseTrackerResult,
  type UpcomingHearingsResult,
  type HearingEntry
} from '../lib/api';

const COURTS = [
  { id: 'delhi_hc', name: 'Delhi High Court' },
  { id: 'bombay_hc', name: 'Bombay High Court' },
  { id: 'madras_hc', name: 'Madras High Court' },
  { id: 'calcutta_hc', name: 'Calcutta High Court' },
  { id: 'karnataka_hc', name: 'Karnataka High Court' },
  { id: 'allahabad_hc', name: 'Allahabad High Court' },
  { id: 'gujarat_hc', name: 'Gujarat High Court' },
  { id: 'rajasthan_hc', name: 'Rajasthan High Court' },
  { id: 'supreme_court', name: 'Supreme Court of India' },
];

type SearchMode = 'cnr' | 'case_number';
type ViewTab = 'today' | 'week' | 'month' | 'history';

export default function CaseTracker() {
  const [searchMode, setSearchMode] = useState<SearchMode>('cnr');
  const [cnrInput, setCnrInput] = useState('');
  const [caseType, setCaseType] = useState('');
  const [caseNumber, setCaseNumber] = useState('');
  const [caseYear, setCaseYear] = useState(new Date().getFullYear().toString());
  const [selectedCourt, setSelectedCourt] = useState('delhi_hc');
  const [loading, setLoading] = useState(false);
  const [caseData, setCaseData] = useState<CaseTrackerResult | null>(null);
  const [hearingData, setHearingData] = useState<UpcomingHearingsResult | null>(null);
  const [activeTab, setActiveTab] = useState<ViewTab>('week');
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (searchMode === 'cnr' && !cnrInput.trim()) return;
    if (searchMode === 'case_number' && (!caseType || !caseNumber || !caseYear)) return;

    setLoading(true);
    setError('');
    setCaseData(null);
    setHearingData(null);

    try {
      let result: CaseTrackerResult;

      if (searchMode === 'cnr') {
        result = await searchByCNR(cnrInput.trim());
      } else {
        result = await searchByCaseNumber({
          case_type: caseType,
          case_number: caseNumber,
          year: caseYear,
          court: selectedCourt
        });
      }

      setCaseData(result);

      // Also fetch upcoming hearings if CNR search
      if (searchMode === 'cnr' && result.success) {
        try {
          const upcoming = await getUpcomingHearings(cnrInput.trim(), 30);
          setHearingData(upcoming);
        } catch (e) {
          // Upcoming hearings optional
        }
      }

    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch case data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return 'N/A';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const isToday = (dateStr: string) => {
    const today = new Date().toDateString();
    try {
      return new Date(dateStr).toDateString() === today;
    } catch { return false; }
  };

  const isThisWeek = (dateStr: string) => {
    const now = new Date();
    const weekEnd = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    try {
      const d = new Date(dateStr);
      return d >= now && d <= weekEnd;
    } catch { return false; }
  };

  const getStatusColor = (status: string) => {
    const s = status?.toLowerCase() || '';
    if (s.includes('disposed') || s.includes('decided')) return 'text-green-600 bg-green-50';
    if (s.includes('pending')) return 'text-yellow-600 bg-yellow-50';
    if (s.includes('fresh') || s.includes('new')) return 'text-blue-600 bg-blue-50';
    return 'text-gray-600 bg-gray-50';
  };

  const HearingCard = ({ hearing, highlight }: { hearing: HearingEntry; highlight?: boolean }) => (
    <div className={`p-3 rounded-lg border ${highlight ? 'border-blue-300 bg-blue-50' : 'border-gray-200 bg-white'}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className={`w-4 h-4 ${highlight ? 'text-blue-600' : 'text-gray-500'}`} />
          <span className={`font-semibold ${highlight ? 'text-blue-800' : 'text-gray-800'}`}>
            {formatDate(hearing.date)}
          </span>
          {isToday(hearing.date) && (
            <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full font-medium">TODAY</span>
          )}
          {!isToday(hearing.date) && isThisWeek(hearing.date) && (
            <span className="px-2 py-0.5 bg-orange-100 text-orange-700 text-xs rounded-full font-medium">THIS WEEK</span>
          )}
        </div>
        {hearing.purpose && (
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">{hearing.purpose}</span>
        )}
      </div>
      {hearing.judge && (
        <p className="text-xs text-gray-500 mt-1">Judge: {hearing.judge}</p>
      )}
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <Scale className="w-8 h-8 text-blue-600" />
          Live Case Tracker
        </h1>
        <p className="text-gray-600 mt-1">
          Track hearing dates across all Indian courts in real-time
        </p>
      </div>

      {/* Search Mode Toggle */}
      <div className="flex gap-2 p-1 bg-gray-100 rounded-lg w-fit">
        <button
          onClick={() => setSearchMode('cnr')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
            searchMode === 'cnr' ? 'bg-white shadow text-blue-600' : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          By CNR Number
        </button>
        <button
          onClick={() => setSearchMode('case_number')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
            searchMode === 'case_number' ? 'bg-white shadow text-blue-600' : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          By Case Number
        </button>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        {searchMode === 'cnr' ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CNR Number (16-digit)
              </label>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={cnrInput}
                  onChange={(e) => setCnrInput(e.target.value.toUpperCase())}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="e.g., DLHC010123456789"
                  maxLength={16}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-lg tracking-wider"
                />
                <button
                  onClick={handleSearch}
                  disabled={loading || !cnrInput.trim()}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
                >
                  {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                  Search
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Find your CNR number on your case documents or at{' '}
                <a href="https://services.ecourts.gov.in" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                  services.ecourts.gov.in
                </a>
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Case Type</label>
                <input
                  type="text"
                  value={caseType}
                  onChange={(e) => setCaseType(e.target.value.toUpperCase())}
                  placeholder="e.g., CO, CS, WP"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Case Number</label>
                <input
                  type="text"
                  value={caseNumber}
                  onChange={(e) => setCaseNumber(e.target.value)}
                  placeholder="e.g., 448"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                <input
                  type="text"
                  value={caseYear}
                  onChange={(e) => setCaseYear(e.target.value)}
                  placeholder="e.g., 2022"
                  maxLength={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Court</label>
                <select
                  value={selectedCourt}
                  onChange={(e) => setSelectedCourt(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {COURTS.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <button
              onClick={handleSearch}
              disabled={loading || !caseType || !caseNumber || !caseYear}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
            >
              {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              Search Case
            </button>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3"
        >
          <AlertCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </motion.div>
      )}

      {/* Results */}
      <AnimatePresence>
        {caseData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            {/* Case Summary Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    {caseData.case_title || `${caseData.case_type || ''} ${caseData.filing_number || caseData.cnr_number || ''}`}
                  </h2>
                  <p className="text-gray-500 text-sm mt-1">
                    {caseData.court || COURTS.find(c => c.id === selectedCourt)?.name}
                  </p>
                </div>
                {caseData.case_status && (
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(caseData.case_status)}`}>
                    {caseData.case_status}
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {caseData.cnr_number && (
                  <div>
                    <p className="text-xs text-gray-500">CNR Number</p>
                    <p className="font-mono font-medium text-gray-900">{caseData.cnr_number}</p>
                  </div>
                )}
                {caseData.filing_number && (
                  <div>
                    <p className="text-xs text-gray-500">Filing Number</p>
                    <p className="font-medium text-gray-900">{caseData.filing_number}</p>
                  </div>
                )}
                {caseData.filing_date && (
                  <div>
                    <p className="text-xs text-gray-500">Filing Date</p>
                    <p className="font-medium text-gray-900">{formatDate(caseData.filing_date)}</p>
                  </div>
                )}
                {caseData.judge && (
                  <div>
                    <p className="text-xs text-gray-500">Judge</p>
                    <p className="font-medium text-gray-900">{caseData.judge}</p>
                  </div>
                )}
                {caseData.petitioner && (
                  <div>
                    <p className="text-xs text-gray-500">Petitioner</p>
                    <p className="font-medium text-gray-900 truncate">{caseData.petitioner}</p>
                  </div>
                )}
                {caseData.case_stage && (
                  <div>
                    <p className="text-xs text-gray-500">Current Stage</p>
                    <p className="font-medium text-gray-900">{caseData.case_stage}</p>
                  </div>
                )}
              </div>

              {/* Next Hearing Highlight */}
              {caseData.next_hearing_date && (
                <div className={`mt-4 p-4 rounded-lg border-2 ${
                  isToday(caseData.next_hearing_date)
                    ? 'border-red-400 bg-red-50'
                    : isThisWeek(caseData.next_hearing_date)
                    ? 'border-orange-400 bg-orange-50'
                    : 'border-blue-400 bg-blue-50'
                }`}>
                  <div className="flex items-center gap-2">
                    <Clock className={`w-5 h-5 ${
                      isToday(caseData.next_hearing_date) ? 'text-red-600' :
                      isThisWeek(caseData.next_hearing_date) ? 'text-orange-600' : 'text-blue-600'
                    }`} />
                    <span className="font-semibold text-gray-900">Next Hearing:</span>
                    <span className={`text-lg font-bold ${
                      isToday(caseData.next_hearing_date) ? 'text-red-700' :
                      isThisWeek(caseData.next_hearing_date) ? 'text-orange-700' : 'text-blue-700'
                    }`}>
                      {formatDate(caseData.next_hearing_date)}
                    </span>
                    {isToday(caseData.next_hearing_date) && (
                      <span className="px-2 py-0.5 bg-red-600 text-white text-xs rounded-full font-bold animate-pulse">
                        TODAY!
                      </span>
                    )}
                    {!isToday(caseData.next_hearing_date) && isThisWeek(caseData.next_hearing_date) && (
                      <span className="px-2 py-0.5 bg-orange-500 text-white text-xs rounded-full font-bold">
                        THIS WEEK
                      </span>
                    )}
                  </div>
                  {caseData.case_stage && (
                    <p className="text-sm text-gray-600 mt-1 ml-7">Purpose: {caseData.case_stage}</p>
                  )}
                </div>
              )}
            </div>

            {/* Hearing Timeline Tabs */}
            {hearingData && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Hearing Schedule</h3>

                {/* Tab Navigation */}
                <div className="flex gap-1 p-1 bg-gray-100 rounded-lg mb-4 w-fit">
                  {[
                    { id: 'today', label: 'Today', icon: Clock, count: hearingData.today.length },
                    { id: 'week', label: 'This Week', icon: CalendarDays, count: hearingData.this_week.length },
                    { id: 'month', label: 'This Month', icon: CalendarRange, count: hearingData.this_month.length },
                    { id: 'history', label: 'History', icon: History, count: hearingData.hearing_history.length },
                  ].map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as ViewTab)}
                      className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                        activeTab === tab.id ? 'bg-white shadow text-blue-600' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      <tab.icon className="w-3.5 h-3.5" />
                      {tab.label}
                      {tab.count > 0 && (
                        <span className={`px-1.5 py-0.5 rounded-full text-xs ${
                          activeTab === tab.id ? 'bg-blue-100 text-blue-700' : 'bg-gray-200 text-gray-600'
                        }`}>
                          {tab.count}
                        </span>
                      )}
                    </button>
                  ))}
                </div>

                {/* Tab Content */}
                <div className="space-y-2">
                  {activeTab === 'today' && (
                    hearingData.today.length > 0 ? (
                      hearingData.today.map((h, i) => <HearingCard key={i} hearing={h} highlight />)
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <Clock className="w-8 h-8 mx-auto mb-2 opacity-30" />
                        <p>No hearings scheduled for today</p>
                        {hearingData.next_hearing && (
                          <p className="text-sm mt-1">Next hearing: {formatDate(hearingData.next_hearing)}</p>
                        )}
                      </div>
                    )
                  )}

                  {activeTab === 'week' && (
                    hearingData.this_week.length > 0 ? (
                      hearingData.this_week.map((h, i) => <HearingCard key={i} hearing={h} highlight={isToday(h.date)} />)
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <CalendarDays className="w-8 h-8 mx-auto mb-2 opacity-30" />
                        <p>No hearings this week</p>
                        {hearingData.next_hearing && (
                          <p className="text-sm mt-1">Next hearing: {formatDate(hearingData.next_hearing)}</p>
                        )}
                      </div>
                    )
                  )}

                  {activeTab === 'month' && (
                    hearingData.this_month.length > 0 ? (
                      hearingData.this_month.map((h, i) => <HearingCard key={i} hearing={h} highlight={isToday(h.date)} />)
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <CalendarRange className="w-8 h-8 mx-auto mb-2 opacity-30" />
                        <p>No hearings this month</p>
                        {hearingData.next_hearing && (
                          <p className="text-sm mt-1">Next hearing: {formatDate(hearingData.next_hearing)}</p>
                        )}
                      </div>
                    )
                  )}

                  {activeTab === 'history' && (
                    hearingData.hearing_history.length > 0 ? (
                      hearingData.hearing_history.map((h, i) => <HearingCard key={i} hearing={h} />)
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <History className="w-8 h-8 mx-auto mb-2 opacity-30" />
                        <p>No hearing history available</p>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

            {/* Info Note */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 mt-0.5" />
              <div className="text-sm text-blue-800">
                <strong>Data Source:</strong> eCourts India (ecourts.gov.in) — Official Government of India court data.
                For the most accurate real-time data, also check{' '}
                <a href="https://services.ecourts.gov.in" target="_blank" rel="noopener noreferrer" className="underline">
                  services.ecourts.gov.in
                </a>
                {' '}directly.
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick Guide */}
      {!caseData && !loading && (
        <div className="bg-gray-50 rounded-xl border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-3">How to find your CNR Number</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div className="flex items-start gap-2">
              <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">1</span>
              <p>Check your court documents — CNR is printed on all official case papers</p>
            </div>
            <div className="flex items-start gap-2">
              <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">2</span>
              <p>Visit <a href="https://services.ecourts.gov.in" target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">services.ecourts.gov.in</a> and search by party name</p>
            </div>
            <div className="flex items-start gap-2">
              <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">3</span>
              <p>Ask your advocate — they have the CNR number for all your cases</p>
            </div>
          </div>

          <div className="mt-4 p-3 bg-white rounded-lg border border-gray-200">
            <p className="text-xs text-gray-500 font-medium mb-2">CNR Format Examples:</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs font-mono">
              <span className="bg-gray-100 px-2 py-1 rounded">DLHC01 + 10 digits</span>
              <span className="bg-gray-100 px-2 py-1 rounded">MHBM01 + 10 digits</span>
              <span className="bg-gray-100 px-2 py-1 rounded">TNCH01 + 10 digits</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
