'use client';

import { useState } from 'react';
import { useMsal } from '@azure/msal-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { linkAPI } from '@/lib/api';
import { isTestMode } from '@/lib/testConfig';
import { CreateLinkForm } from './CreateLinkForm';
import { LinkList } from './LinkList';
import { Header } from './Header';
import { Analytics } from './Analytics';
import { Link2, Plus, List, BarChart3 } from 'lucide-react';

type TabType = 'create' | 'links' | 'analytics';

export function LinkDashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('create');
  const [selectedLinkId, setSelectedLinkId] = useState<string | null>(null);
  const { accounts } = useMsal();
  const queryClient = useQueryClient();

  // No need to manually store tokens - the API interceptor handles ID token acquisition

  const { data: links = [], isLoading } = useQuery({
    queryKey: ['links'],
    queryFn: async () => {
      const response = await linkAPI.getLinks();
      return response.data;
    },
    enabled: isTestMode || !!accounts.length,
  });

  const createLinkMutation = useMutation({
    mutationFn: linkAPI.createLink,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['links'] });
      setActiveTab('links');
    },
  });

  const deleteLinkMutation = useMutation({
    mutationFn: linkAPI.deleteLink,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['links'] });
    },
  });

  const tabs = [
    { id: 'create' as TabType, label: 'Create Link', icon: Plus },
    { id: 'links' as TabType, label: 'My Links', icon: List },
    { id: 'analytics' as TabType, label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-6">
            <Link2 className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">Link Shortener</h1>
          </div>
          
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === tab.id
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="bg-white rounded-lg shadow">
          {activeTab === 'create' && (
            <CreateLinkForm
              onSubmit={(data: { original_url: string; custom_short_code?: string; description?: string }) => createLinkMutation.mutate(data)}
              isLoading={createLinkMutation.isPending}
            />
          )}
          
          {activeTab === 'links' && (
            <LinkList
              links={links}
              isLoading={isLoading}
              onDelete={(id: string) => deleteLinkMutation.mutate(id)}
              onViewAnalytics={(id: string) => {
                setSelectedLinkId(id);
                setActiveTab('analytics');
              }}
            />
          )}
          
          {activeTab === 'analytics' && (
            <Analytics
              linkId={selectedLinkId}
              links={links}
              onSelectLink={setSelectedLinkId}
            />
          )}
        </div>
      </main>
    </div>
  );
}
