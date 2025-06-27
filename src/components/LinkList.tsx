'use client';

import { useState } from 'react';
import { Link, Copy, Trash2, BarChart3, ExternalLink, Check, Loader2 } from 'lucide-react';
import type { Link as LinkType } from '@/lib/api';

interface LinkListProps {
  links: LinkType[];
  isLoading: boolean;
  onDelete: (id: string) => void;
  onViewAnalytics: (id: string) => void;
}

export function LinkList({ links, isLoading, onDelete, onViewAnalytics }: LinkListProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" data-testid="loading-spinner" />
        </div>
      </div>
    );
  }

  if (links.length === 0) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <Link className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No links yet</h3>
          <p className="text-gray-600">Create your first short link to get started.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex items-center space-x-2 mb-6">
        <Link className="h-5 w-5 text-blue-600" />
        <h2 className="text-lg font-medium text-gray-900">Your Links</h2>
        <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-sm">
          {links.length}
        </span>
      </div>

      <div className="space-y-4">
        {links.map((link) => (
          <div key={link.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-2">
                  <h3 className="text-lg font-medium text-gray-900 truncate">
                    {link.description || 'Untitled Link'}
                  </h3>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {link.click_count} clicks
                  </span>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">Short URL:</span>
                    <a
                      href={link.short_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 font-medium text-sm flex items-center space-x-1"
                    >
                      <span>{link.short_url}</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                    <button
                      onClick={() => copyToClipboard(link.short_url, link.id)}
                      className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      {copiedId === link.id ? (
                        <Check className="h-4 w-4 text-green-500" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">Original URL:</span>
                    <a
                      href={link.original_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-700 hover:text-gray-900 text-sm truncate max-w-md"
                      title={link.original_url}
                    >
                      {link.original_url}
                    </a>
                  </div>
                  
                  <div className="text-xs text-gray-500">
                    Created on {formatDate(link.created_at)}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                <button
                  onClick={() => onViewAnalytics(link.id)}
                  className="flex items-center space-x-1 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                  title="View Analytics"
                >
                  <BarChart3 className="h-4 w-4" />
                  <span>Analytics</span>
                </button>
                
                <button
                  onClick={() => onDelete(link.id)}
                  className="flex items-center space-x-1 px-3 py-2 text-sm text-red-600 hover:text-red-900 hover:bg-red-50 rounded-md transition-colors"
                  title="Delete Link"
                >
                  <Trash2 className="h-4 w-4" />
                  <span>Delete</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
