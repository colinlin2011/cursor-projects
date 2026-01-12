"use client";

import { useState } from 'react';
import { supabase } from '@/lib/supabase';

interface AddPhotonModalProps {
  onClose: () => void;
  onSubmitSuccess: () => void;
  templates: any[];
  companyColors: Record<string, string>;
}

export default function AddPhotonModal({ onClose, onSubmitSuccess, templates, companyColors }: AddPhotonModalProps) {
  const [selectedTemplate, setSelectedTemplate] = useState(templates[0]);
  const [content, setContent] = useState('');
  const [authorName, setAuthorName] = useState('');
  const [authorCompany, setAuthorCompany] = useState('');
  const [authorProfession, setAuthorProfession] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setIsSubmitting(true);
    try {
      const { error } = await supabase
        .from('photons')
        .insert([{
          content,
          template_type: selectedTemplate.id,
          author_name: authorName || '匿名同行',
          author_company: authorCompany || '',
          author_profession: authorProfession || '',
          likes_count: 0
        }]);

      if (error) throw error;
      
      alert('✨ 光子发射成功！你的声音已加入行业光谱。');
      onSubmitSuccess();
      onClose();
    } catch (error) {
      console.error('提交失败:', error);
      alert('❌ 提交失败，请稍后重试');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* 背景遮罩 */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* 模态框内容 */}
      <div className="relative w-full max-w-2xl mx-4">
        <div className="bg-gradient-to-br from-gray-900 to-black border border-white/10 rounded-3xl overflow-hidden">
          {/* 头部 */}
          <div className="p-8 border-b border-white/10">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white">✨ 发射新光子</h2>
                <p className="text-gray-400 mt-2">你的声音将永远留在行业光谱中</p>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/10 rounded-xl transition-colors"
              >
                <span className="text-2xl">×</span>
              </button>
            </div>
          </div>
          
          {/* 表单内容 */}
          <form onSubmit={handleSubmit} className="p-8">
            {/* 模板选择 */}
            <div className="mb-8">
              <label className="block text-gray-300 mb-4 text-sm font-medium">选择光子类型</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {templates.map(template => (
                  <button
                    key={template.id}
                    type="button"
                    onClick={() => {
                      setSelectedTemplate(template);
                      if (!content) setContent(template.example);
                    }}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      selectedTemplate.id === template.id 
                        ? `${template.borderColor} ${template.color} scale-105` 
                        : 'border-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="text-center">
                      <div className="text-2xl mb-1">{template.icon}</div>
                      <div className={`text-xs font-medium ${
                        selectedTemplate.id === template.id ? template.textColor : 'text-gray-400'
                      }`}>
                        {template.name}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
            
            {/* 内容输入 */}
            <div className="mb-6">
              <label className="block text-gray-300 mb-3 text-sm font-medium">
                📝 {selectedTemplate.prompt}
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full h-40 bg-black/40 border border-white/10 rounded-xl p-4 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50 transition-all resize-none"
                placeholder={selectedTemplate.example}
                disabled={isSubmitting}
              />
            </div>
            
            {/* 作者信息 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div>
                <label className="block text-gray-300 mb-2 text-sm">👤 称呼/昵称</label>
                <input
                  type="text"
                  value={authorName}
                  onChange={(e) => setAuthorName(e.target.value)}
                  className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500/50 transition"
                  placeholder="匿名同行"
                  disabled={isSubmitting}
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2 text-sm">🏢 公司（可选）</label>
                <input
                  type="text"
                  value={authorCompany}
                  onChange={(e) => setAuthorCompany(e.target.value)}
                  className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500/50 transition"
                  placeholder="如：华为、蔚来..."
                  disabled={isSubmitting}
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2 text-sm">💼 职业（可选）</label>
                <input
                  type="text"
                  value={authorProfession}
                  onChange={(e) => setAuthorProfession(e.target.value)}
                  className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500/50 transition"
                  placeholder="如：感知算法工程师"
                  disabled={isSubmitting}
                />
              </div>
            </div>
            
            {/* 快速公司选择 */}
            <div className="mb-8">
              <label className="block text-gray-300 mb-3 text-sm">🏢 快速选择公司</label>
              <div className="flex flex-wrap gap-2">
                {Object.keys(companyColors).map(company => (
                  <button
                    key={company}
                    type="button"
                    onClick={() => setAuthorCompany(company)}
                    className={`px-3 py-2 rounded-lg text-sm border transition-all ${
                      companyColors[company]
                    } ${
                      authorCompany === company ? 'bg-white/10' : 'bg-black/30'
                    } hover:scale-105`}
                  >
                    {company}
                  </button>
                ))}
              </div>
            </div>
            
            {/* 底部按钮 */}
            <div className="flex justify-end gap-4 pt-6 border-t border-white/10">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-3 bg-white/5 hover:bg-white/10 rounded-xl font-medium text-white transition-colors"
                disabled={isSubmitting}
              >
                取消
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !content.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl font-medium text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
              >
                {isSubmitting ? (
                  <span className="flex items-center gap-2">
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    发射中...
                  </span>
                ) : (
                  '🚀 发射光子'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
