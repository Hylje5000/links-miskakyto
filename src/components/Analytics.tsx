'use client';

import { useQuery } from '@tanstack/react-query';
import { linkAPI, type Link, type Analytics as AnalyticsType } from '@/lib/api';
import { BarChart3, Users, Calendar, TrendingUp, Loader2 } from 'lucide-react';

interface AnalyticsProps {
  linkId: string | null;
  links: Link[];
  onSelectLink: (id: string) => void;
}

export function Analytics({ linkId, links, onSelectLink }: AnalyticsProps) {
  const { data: analytics, isLoading } = useQuery<AnalyticsType | null>({
    queryKey: ['analytics', linkId],
    queryFn: async () => {
      if (!linkId) return null;
      const response = await linkAPI.getLinkAnalytics(linkId);
      return response.data;
    },
    enabled: !!linkId,
  });

  const selectedLink = links.find(link => link.id === linkId);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getClicksByDate = (clicks: AnalyticsType['recent_clicks']) => {
    const clicksByDate: Record<string, number> = {};
    
    clicks.forEach(click => {
      const date = new Date(click.clicked_at).toDateString();
      clicksByDate[date] = (clicksByDate[date] || 0) + 1;
    });
    
    return Object.entries(clicksByDate)
      .sort(([a], [b]) => new Date(a).getTime() - new Date(b).getTime())
      .slice(-7); // Last 7 days
  };

  return (
    <div className="p-6">
      <div className="flex items-center space-x-2 mb-6">
        <BarChart3 className="h-5 w-5 text-blue-600" />
        <h2 className="text-lg font-medium text-gray-900">Analytics</h2>
      </div>

      {/* Link Selection */}
      <div className="mb-6">
        <label htmlFor="link-select" className="block text-sm font-medium text-gray-700 mb-2">
          Select Link
        </label>
        <select
          id="link-select"
          value={linkId || ''}
          onChange={(e) => onSelectLink(e.target.value)}
          className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Choose a link to view analytics</option>
          {links.map((link) => (
            <option key={link.id} value={link.id}>
              {link.description || link.short_code} - {link.click_count} clicks
            </option>
          ))}
        </select>
      </div>

      {!linkId && (
        <div className="text-center py-12">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Select a link to view analytics</h3>
          <p className="text-gray-600">Choose a link from the dropdown above to see detailed analytics.</p>
        </div>
      )}

      {linkId && isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      )}

      {linkId && selectedLink && analytics && (
        <div className="space-y-6">
          {/* Link Overview */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">
              {selectedLink.description || 'Untitled Link'}
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              <span className="font-medium">Short URL:</span> {selectedLink.short_url}
            </p>
            <p className="text-sm text-gray-600 truncate">
              <span className="font-medium">Original URL:</span> {selectedLink.original_url}
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">Total Clicks</span>
              </div>
              <div className="mt-2">
                <span className="text-2xl font-bold text-blue-900">{analytics.total_clicks}</span>
              </div>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-green-900">Created</span>
              </div>
              <div className="mt-2">
                <span className="text-sm font-medium text-green-900">
                  {formatDate(selectedLink.created_at)}
                </span>
              </div>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                <span className="text-sm font-medium text-purple-900">Recent Activity</span>
              </div>
              <div className="mt-2">
                <span className="text-sm font-medium text-purple-900">
                  {analytics.recent_clicks.length} clicks in last 100
                </span>
              </div>
            </div>
          </div>

          {/* Daily Clicks Chart */}
          {analytics.recent_clicks.length > 0 && (
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-4">Daily Clicks (Last 7 Days)</h4>
              <div className="space-y-2">
                {getClicksByDate(analytics.recent_clicks).map(([date, count]) => (
                  <div key={date} className="flex items-center space-x-3">
                    <div className="w-20 text-sm text-gray-600">
                      {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </div>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${(count / Math.max(...getClicksByDate(analytics.recent_clicks).map(([, c]) => c))) * 100}%`
                        }}
                      ></div>
                    </div>
                    <div className="w-8 text-sm text-gray-900 text-right">{count}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Clicks */}
          {analytics.recent_clicks.length > 0 && (
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-4">Recent Clicks</h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {analytics.recent_clicks.slice(0, 20).map((click: { clicked_at: string; ip_address: string }, index: number) => (
                  <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                    <div className="text-sm text-gray-600">
                      {formatDate(click.clicked_at)}
                    </div>
                    <div className="text-sm text-gray-900 font-mono">
                      {click.ip_address}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {analytics.recent_clicks.length === 0 && (
            <div className="text-center py-8 border border-gray-200 rounded-lg">
              <Users className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900 mb-1">No clicks yet</h4>
              <p className="text-gray-600 text-sm">Share your link to start tracking clicks.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
