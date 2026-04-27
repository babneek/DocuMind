import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Database,
  Download,
  Search,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Loader,
  BookOpen,
  Scale,
  Building2,
  Briefcase,
  Home,
  Gavel,
  Shield,
  Receipt,
  Landmark,
  ShoppingCart
} from 'lucide-react';
import {
  getCaseLawStats,
  searchCaseLaw,
  triggerCaseImport,
  getAvailableDomains,
  type CaseLawStats,
  type CaseLawCase,
  type CaseLawSearchRequest,
  type DomainInfo
} from '../lib/api';

const CATEGORIES = [
  { name: 'Contract Law', icon: BookOpen, color: 'blue' },
  { name: 'Corporate Law', icon: Building2, color: 'purple' },
  { name: 'Intellectual Property', icon: Briefcase, color: 'pink' },
  { name: 'Employment Law', icon: Briefcase, color: 'green' },
  { name: 'Real Estate', icon: Home, color: 'orange' },
  { name: 'Arbitration', icon: Gavel, color: 'red' },
  { name: 'Cyber Law', icon: Shield, color: 'indigo' },
  { name: 'Tax Law', icon: Receipt, color: 'yellow' },
  { name: 'Banking & Finance', icon: Landmark, color: 'teal' },
  { name: 'Consumer Protection', icon: ShoppingCart, color: 'cyan' }
];

export default function CaseLawAdmin() {
  const [stats, setStats] = useState<CaseLawStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [importStatus, setImportStatus] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CaseLawCase[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [availableDomains, setAvailableDomains] = useState<DomainInfo[]>([]);

  useEffect(() => {
    loadStats();
    loadAvailableDomains();
  }, []);

  const loadAvailableDomains = async () => {
    try {
      const data = await getAvailableDomains();
      setAvailableDomains(data.domains);
    } catch (error) {
      console.error('Failed to load domains:', error);
    }
  };

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await getCaseLawStats();
      setStats(data);
    } catch (error: any) {
      console.error('Failed to load stats:', error);
      // Set default empty stats on error
      setStats({
        total_cases: 0,
        courts: [],
        legal_areas: [],
        categories: {},
        importance_distribution: {
          Landmark: 0,
          Important: 0,
          Regular: 0
        },
        last_updated: ''
      });
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (mode: 'foundation' | 'domain', domain?: string) => {
    if (importing) return;

    const caseCount = mode === 'foundation' ? 100 : 10;
    const timeEstimate = mode === 'foundation' ? '5-10 minutes' : '2-3 minutes';
    
    const confirmMsg = mode === 'foundation'
      ? `Import ${caseCount} REAL cases from Indian Kanoon across all domains? This will take ${timeEstimate}.`
      : `Import 10 REAL ${domain} cases from Indian Kanoon? This will take ${timeEstimate}.`;

    if (!confirm(confirmMsg)) return;

    try {
      setImporting(true);
      setImportStatus('Scraping real cases from Indian Kanoon...');
      
      const response = await triggerCaseImport({ mode, domain });
      
      setImportStatus(response.message);
      
      // Refresh stats after a longer delay for scraping
      setTimeout(() => {
        loadStats();
        setImporting(false);
        setImportStatus('');
      }, mode === 'foundation' ? 10000 : 5000);
      
    } catch (error: any) {
      console.error('Import failed:', error);
      setImportStatus(`Error: ${error.response?.data?.detail || error.message}`);
      setTimeout(() => {
        setImporting(false);
        setImportStatus('');
      }, 5000);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setSearching(true);
      const request: CaseLawSearchRequest = {
        query: searchQuery,
        category: selectedCategory || undefined,
        top_k: 10
      };
      
      const response = await searchCaseLaw(request);
      setSearchResults(response.cases);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearching(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Database className="w-8 h-8 text-blue-600" />
            Case Law Knowledge Base
          </h1>
          <p className="text-gray-600 mt-1">
            Manage and import Indian legal cases across all domains
          </p>
        </div>
      </div>

      {/* Import Status Alert */}
      {importStatus && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-4 rounded-lg flex items-center gap-3 ${
            importing
              ? 'bg-blue-50 border border-blue-200'
              : 'bg-green-50 border border-green-200'
          }`}
        >
          {importing ? (
            <Loader className="w-5 h-5 animate-spin text-blue-600" />
          ) : (
            <CheckCircle className="w-5 h-5 text-green-600" />
          )}
          <span className={importing ? 'text-blue-800' : 'text-green-800'}>
            {importStatus}
          </span>
        </motion.div>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Cases</p>
              <p className="text-3xl font-bold mt-1">{stats?.total_cases || 0}</p>
            </div>
            <Scale className="w-12 h-12 text-blue-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Categories</p>
              <p className="text-3xl font-bold mt-1">
                {stats?.categories ? Object.keys(stats.categories).length : 0}
              </p>
            </div>
            <BookOpen className="w-12 h-12 text-purple-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Landmark Cases</p>
              <p className="text-3xl font-bold mt-1">
                {stats?.importance_distribution?.Landmark || 0}
              </p>
            </div>
            <TrendingUp className="w-12 h-12 text-green-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Courts</p>
              <p className="text-3xl font-bold mt-1">
                {stats?.courts?.length || 0}
              </p>
            </div>
            <Landmark className="w-12 h-12 text-orange-200" />
          </div>
        </motion.div>
      </div>

      {/* Quick Import Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Download className="w-5 h-5 text-blue-600" />
          Import Real Cases from Indian Kanoon
        </h2>
        
        <div className="grid grid-cols-1 gap-4">
          <button
            onClick={() => handleImport('foundation')}
            disabled={importing}
            className="p-4 border-2 border-blue-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
          >
            <div className="flex items-start gap-3">
              <CheckCircle className="w-6 h-6 text-blue-600 mt-1" />
              <div>
                <h3 className="font-semibold text-gray-900">Import All Domains (100 Cases)</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Scrape 10 real cases per domain from Indian Kanoon
                </p>
                <p className="text-xs text-gray-500 mt-2">⏱️ 5-10 minutes • 🌐 Live scraping</p>
              </div>
            </div>
          </button>
        </div>

        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-blue-800">
            <strong>Note:</strong> Import scrapes REAL cases from Indian Kanoon and uses AI to categorize them. 
            This takes a few minutes. You can continue using the app while it runs in the background.
          </div>
        </div>
      </div>

      {/* Domain-Specific Import */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Import by Domain (10 Real Cases Each)
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {availableDomains.map((domain) => {
            const Icon = CATEGORIES.find(c => c.name === domain.name)?.icon || BookOpen;
            const color = CATEGORIES.find(c => c.name === domain.name)?.color || 'gray';
            const currentCount = stats?.categories?.[domain.name] || 0;
            
            return (
              <button
                key={domain.name}
                onClick={() => handleImport('domain', domain.name)}
                disabled={importing}
                className={`p-4 border-2 rounded-lg hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left border-${color}-200 hover:border-${color}-400 hover:bg-${color}-50`}
              >
                <Icon className={`w-6 h-6 text-${color}-600 mb-2`} />
                <h3 className="font-medium text-gray-900 text-sm">{domain.name}</h3>
                <p className="text-xs text-gray-500 mt-1">
                  {currentCount} in DB • Import 10 real cases
                </p>
                <p className="text-xs text-blue-600 mt-1">⏱️ 2-3 min</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Search Cases */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Search className="w-5 h-5 text-blue-600" />
          Search Case Law
        </h2>
        
        <div className="flex gap-3 mb-4">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search for cases... (e.g., 'software contract breach')"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          
          <select
            value={selectedCategory || ''}
            onChange={(e) => setSelectedCategory(e.target.value || null)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            {CATEGORIES.map((cat) => (
              <option key={cat.name} value={cat.name}>{cat.name}</option>
            ))}
          </select>
          
          <button
            onClick={handleSearch}
            disabled={searching || !searchQuery.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {searching ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Search
          </button>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="space-y-3 mt-6">
            <h3 className="font-semibold text-gray-900">
              Found {searchResults.length} case(s)
            </h3>
            {searchResults.map((caseItem) => (
              <motion.div
                key={caseItem.case_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{caseItem.case_name}</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {caseItem.citation} • {caseItem.court} • {caseItem.date}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                        {caseItem.category}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded ${
                        caseItem.importance === 'Landmark'
                          ? 'bg-yellow-100 text-yellow-700'
                          : caseItem.importance === 'Important'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {caseItem.importance}
                      </span>
                      <span className="text-xs text-gray-500">
                        Relevance: {(caseItem.relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mt-2 line-clamp-2">
                      {caseItem.excerpt}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Database Details */}
      {stats && stats.categories && Object.keys(stats.categories).length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Database Breakdown
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(stats.categories).map(([category, count]) => (
              <div key={category} className="p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">{category}</p>
                <p className="text-2xl font-bold text-gray-900">{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
