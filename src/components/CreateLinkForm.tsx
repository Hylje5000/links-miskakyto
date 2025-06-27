'use client';

import { useState } from 'react';
import { Link, Loader2, Copy, Check } from 'lucide-react';

interface CreateLinkFormProps {
  onSubmit: (data: { original_url: string; custom_short_code?: string; description?: string }) => void;
  isLoading: boolean;
}

export function CreateLinkForm({ onSubmit, isLoading }: CreateLinkFormProps) {
  const [originalUrl, setOriginalUrl] = useState('');
  const [customCode, setCustomCode] = useState('');
  const [description, setDescription] = useState('');
  const [lastCreatedUrl, setLastCreatedUrl] = useState('');
  const [copied, setCopied] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!originalUrl.trim()) return;
    
    const data = {
      original_url: originalUrl.trim(),
      custom_short_code: customCode.trim() || undefined,
      description: description.trim() || undefined,
    };
    
    onSubmit(data);
    setLastCreatedUrl(''); // Clear previous URL
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-center space-x-2 mb-6">
        <Link className="h-5 w-5 text-blue-600" />
        <h2 className="text-lg font-medium text-gray-900">Create Short Link</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="original-url" className="block text-sm font-medium text-gray-700 mb-2">
            Original URL *
          </label>
          <input
            id="original-url"
            type="url"
            value={originalUrl}
            onChange={(e) => setOriginalUrl(e.target.value)}
            placeholder="https://example.com/very-long-url"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label htmlFor="custom-code" className="block text-sm font-medium text-gray-700 mb-2">
            Custom Short Code (optional)
          </label>
          <input
            id="custom-code"
            type="text"
            value={customCode}
            onChange={(e) => setCustomCode(e.target.value)}
            placeholder="my-custom-link"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            pattern="[a-zA-Z0-9\-_]+"
            title="Only letters, numbers, hyphens, and underscores are allowed"
          />
          <p className="text-xs text-gray-500 mt-1">
            Leave empty to generate automatically
          </p>
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Description (optional)
          </label>
          <input
            id="description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe this link..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div className="flex items-center justify-between pt-4">
          <button
            type="submit"
            disabled={isLoading || !originalUrl.trim()}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Link className="h-4 w-4" />
            )}
            <span>{isLoading ? 'Creating...' : 'Create Short Link'}</span>
          </button>
        </div>
      </form>

      {lastCreatedUrl && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <h3 className="text-sm font-medium text-green-800 mb-2">Link Created Successfully!</h3>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={lastCreatedUrl}
              readOnly
              className="flex-1 px-3 py-2 bg-white border border-green-300 rounded-md text-sm"
            />
            <button
              onClick={() => copyToClipboard(lastCreatedUrl)}
              className="flex items-center space-x-1 px-3 py-2 text-sm text-green-700 hover:text-green-900 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
