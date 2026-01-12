// components/PhotonForm.tsx - 修复版
"use client";

import { useState } from 'react';

interface PhotonTemplate {
  id: string;
  name: string;
  description: string;
  color: string;
  icon: string;
  prompt?: string;
  // 添加 textColor 属性
  textColor?: string;
}

interface CompanyColors {
  [key: string]: string;
}

interface PhotonFormProps {
  onSubmit: (photonData: {
    content: string;
    template_type: string;
    author_name: string;
    author_company: string;
    author_profession: string;
  }) => Promise<void>;
  templates: PhotonTemplate[];
  companyColors: CompanyColors;
}

export default function PhotonForm({ onSubmit, templates, companyColors }: PhotonFormProps) {
  const [photonContent, setPhotonContent] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<PhotonTemplate>(templates[0]);
  const [authorName, setAuthorName] = useState('');
  const [authorCompany, setAuthorCompany] = useState('');
  const [authorProfession, setAuthorProfession] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!photonContent.trim()) {
      setError('请填写光子内容');
      return;
    }
    
    if (photonContent.length > 500) {
      setError('内容不能超过500字');
      return;
    }
    
    if (!authorName.trim()) {
      setError('请填写您的姓名或昵称');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      await onSubmit({
        content: photonContent.trim(),
        template_type: selectedTemplate.id,
        author_name: authorName.trim(),
        author_company: authorCompany.trim() || '其他',
        author_profession: authorProfession.trim()
      });
      
      // 重置表单
      setPhotonContent('');
      setAuthorName('');
      setAuthorCompany('');
      setAuthorProfession('');
    } catch (err) {
      setError('提交失败，请重试');
      console.error('提交失败:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 获取模板的文本颜色（根据背景色自动计算）
  const getTextColor = (template: PhotonTemplate): string => {
    // 如果模板有自定义的 textColor，使用它
    if (template.textColor) return template.textColor;
    
    // 否则根据背景色自动计算合适的文本颜色
    const color = template.color;
    if (color.startsWith('#') && color.length === 7) {
      // 解析十六进制颜色
      const r = parseInt(color.slice(1, 3), 16);
      const g = parseInt(color.slice(3, 5), 16);
      const b = parseInt(color.slice(5, 7), 16);
      
      // 计算亮度
      const brightness = (r * 299 + g * 587 + b * 114) / 1000;
      
      // 根据亮度返回黑色或白色文本
      return brightness > 128 ? '#000000' : '#ffffff';
    }
    
    // 默认返回白色文本
    return '#ffffff';
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 模板选择器 */}
      <div>
        <label className="block text-gray-400 text-sm mb-3">
          <span className="flex items-center gap-2">
            <span>🎯</span>
            <span>选择光子类型</span>
          </span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {templates.map((template) => (
            <button
              key={template.id}
              type="button"
              onClick={() => setSelectedTemplate(template)}
              className={`relative p-3 rounded-xl border transition-all duration-300 ${
                selectedTemplate.id === template.id
                  ? 'scale-105 ring-2 ring-white/30'
                  : 'hover:scale-102 hover:bg-white/5'
              }`}
              style={{
                background: selectedTemplate.id === template.id
                  ? `linear-gradient(135deg, ${template.color}30, ${template.color}10)`
                  : 'transparent',
                borderColor: selectedTemplate.id === template.id
                  ? `${template.color}50`
                  : 'rgba(255, 255, 255, 0.1)'
              }}
            >
              <div className="flex flex-col items-center gap-2">
                <div 
                  className="w-8 h-8 rounded-full flex items-center justify-center"
                  style={{ 
                    backgroundColor: template.color,
                    color: getTextColor(template)
                  }}
                >
                  <span className="text-sm">{template.icon}</span>
                </div>
                <span className={`text-sm font-medium ${
                  selectedTemplate.id === template.id ? 'text-white' : 'text-gray-300'
                }`}>
                  {template.name}
                </span>
                <span className="text-xs text-gray-500 text-center">
                  {template.description}
                </span>
              </div>
              
              {selectedTemplate.id === template.id && (
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-white rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* 内容输入框 */}
      <div>
        <label className="block text-gray-400 text-sm mb-3">
          <span className="flex items-center gap-2">
            <span>✨</span>
            <span>光子内容</span>
          </span>
          {selectedTemplate.prompt && (
            <div className="mt-1 text-xs text-gray-500 italic">
              {selectedTemplate.prompt}
            </div>
          )}
        </label>
        <div className="relative">
          <textarea
            value={photonContent}
            onChange={(e) => setPhotonContent(e.target.value)}
            placeholder="记录您的行业见闻、感悟或预言..."
            maxLength={500}
            rows={4}
            className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/30 resize-none transition-all"
            style={{
              borderColor: selectedTemplate.color + '30'
            }}
          />
          <div className="flex justify-between items-center mt-2">
            <div className="text-gray-500 text-sm">
              正在使用 <span 
                className="font-medium"
                style={{ color: selectedTemplate.color }}
              >{selectedTemplate.name}</span> 模板
            </div>
            <div className="text-gray-500 text-sm">
              {photonContent.length}/500
            </div>
          </div>
        </div>
      </div>

      {/* 作者信息 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-gray-400 text-sm mb-2">
            <span className="flex items-center gap-2">
              <span>👤</span>
              <span>姓名/昵称</span>
            </span>
          </label>
          <input
            type="text"
            value={authorName}
            onChange={(e) => setAuthorName(e.target.value)}
            placeholder="匿名"
            maxLength={20}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/30 transition-all"
          />
        </div>

        <div>
          <label className="block text-gray-400 text-sm mb-2">
            <span className="flex items-center gap-2">
              <span>🏢</span>
              <span>公司</span>
            </span>
          </label>
          <select
            value={authorCompany}
            onChange={(e) => setAuthorCompany(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/30 transition-all appearance-none"
          >
            <option value="">选择公司...</option>
            {Object.keys(companyColors).map((company) => (
              <option key={company} value={company} className="bg-gray-900">
                {company}
              </option>
            ))}
            <option value="其他" className="bg-gray-900">其他</option>
          </select>
        </div>

        <div>
          <label className="block text-gray-400 text-sm mb-2">
            <span className="flex items-center gap-2">
              <span>💼</span>
              <span>职业</span>
            </span>
          </label>
          <select
            value={authorProfession}
            onChange={(e) => setAuthorProfession(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/30 transition-all appearance-none"
          >
            <option value="">选择职业...</option>
            <option value="感知算法工程师" className="bg-gray-900">感知算法工程师</option>
            <option value="规控工程师" className="bg-gray-900">规控工程师</option>
            <option value="系统架构师" className="bg-gray-900">系统架构师</option>
            <option value="产品经理" className="bg-gray-900">产品经理</option>
            <option value="测试工程师" className="bg-gray-900">测试工程师</option>
            <option value="项目经理" className="bg-gray-900">项目经理</option>
            <option value="战略规划" className="bg-gray-900">战略规划</option>
            <option value="其他" className="bg-gray-900">其他</option>
          </select>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-400 text-sm">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* 提交按钮 */}
      <div className="flex justify-end pt-4 border-t border-white/10">
        <button
          type="submit"
          disabled={isSubmitting}
          className="group relative"
        >
          <div 
            className="absolute inset-0 rounded-xl blur-md opacity-70 group-hover:opacity-100 transition-all duration-300"
            style={{ background: selectedTemplate.color }}
          ></div>
          <div 
            className="relative px-8 py-3 rounded-xl font-semibold text-white flex items-center gap-2 hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ 
              background: `linear-gradient(135deg, ${selectedTemplate.color}, ${selectedTemplate.color}80)`
            }}
          >
            {isSubmitting ? (
              <>
                <span className="animate-spin">⏳</span>
                <span>提交中...</span>
              </>
            ) : (
              <>
                <span>✨</span>
                <span>发射光子</span>
              </>
            )}
          </div>
        </button>
      </div>

      {/* 提示信息 */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <div className="text-sm text-blue-400">
          <div className="flex items-start gap-2">
            <span>💡</span>
            <div>
              <p className="font-medium">提交须知</p>
              <ul className="mt-2 space-y-1 text-blue-300/80">
                <li>• 光子内容将公开显示，请勿包含敏感信息</li>
                <li>• 您可以匿名提交，但建议填写真实信息以获得共鸣</li>
                <li>• 光锥计划致力于记录自动驾驶行业的真实声音</li>
                <li>• 所有内容需遵守社区准则</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </form>
  );
}
