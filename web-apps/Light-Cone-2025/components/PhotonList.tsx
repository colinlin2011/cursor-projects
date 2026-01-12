// components/PhotonList.tsx - 完整版
"use client";

import { useState } from 'react';
import { COMPANY_COLORS } from '@/lib/companyColors';

interface Photon {
  id: string | number;
  content: string;
  author: string;
  type: string;
  likes: number;
  time: string;
  company: string;
  color?: string;
  year?: number;
}

interface PhotonListProps {
  photons: Photon[];
}

// 类型名称映射
const TYPE_NAMES: Record<string, string> = {
  'moment': '那个瞬间',
  'prophecy': '预言胶囊',
  'culture': '团队文化',
  'inspiration': '灵光闪现',
  'darkmoment': '至暗时刻',
  'history': '历史记录',
  'onsite': '现场观察'
};

// 类型颜色映射
const TYPE_COLORS: Record<string, string> = {
  'moment': '#3b82f6',
  'prophecy': '#8b5cf6',
  'culture': '#f59e0b',
  'inspiration': '#06b6d4',
  'darkmoment': '#ef4444',
  'history': '#f97316',
  'onsite': '#10b981'
};

export default function PhotonList({ photons }: PhotonListProps) {
  const [sortBy, setSortBy] = useState<'time' | 'likes' | 'company'>('time');
  const [filterType, setFilterType] = useState<string | null>(null);
  const [filterCompany, setFilterCompany] = useState<string | null>(null);

  // 处理排序
  const sortedPhotons = [...photons].sort((a, b) => {
    switch (sortBy) {
      case 'time':
        return new Date(b.time).getTime() - new Date(a.time).getTime();
      case 'likes':
        return b.likes - a.likes;
      case 'company':
        return a.company.localeCompare(b.company);
      default:
        return 0;
    }
  });

  // 处理筛选
  const filteredPhotons = sortedPhotons.filter(photon => {
    if (filterType && photon.type !== filterType) return false;
    if (filterCompany && photon.company !== filterCompany) return false;
    return true;
  });

  // 获取所有公司和类型
  const companies = Array.from(new Set(photons.map(p => p.company)));
  const types = Array.from(new Set(photons.map(p => p.type)));

  return (
    <div className="h-full flex flex-col">
      {/* 标题栏 */}
      <div className="px-8 py-6 border-b border-white/10">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">光子列表</h2>
            <p className="text-gray-400 mt-1">按时间顺序查看所有记录</p>
          </div>
          <div className="text-sm text-gray-500">
            共 {filteredPhotons.length} 个光子
          </div>
        </div>
      </div>

      {/* 控制栏 */}
      <div className="px-8 py-4 border-b border-white/10 bg-gradient-to-r from-white/5 to-transparent">
        <div className="flex flex-wrap gap-4 items-center">
          {/* 排序选择 */}
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-sm">排序:</span>
            <div className="flex bg-white/5 rounded-lg p-1">
              {[
                { id: 'time', label: '时间', icon: '📅' },
                { id: 'likes', label: '共鸣', icon: '💫' },
                { id: 'company', label: '公司', icon: '🏢' }
              ].map((option) => (
                <button
                  key={option.id}
                  onClick={() => setSortBy(option.id as any)}
                  className={`px-3 py-1.5 rounded-md text-sm flex items-center gap-1.5 transition-all ${
                    sortBy === option.id
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <span>{option.icon}</span>
                  <span>{option.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* 类型筛选 */}
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-sm">类型:</span>
            <div className="flex flex-wrap gap-1">
              <button
                onClick={() => setFilterType(null)}
                className={`px-3 py-1.5 rounded-md text-sm ${
                  !filterType
                    ? 'bg-white/20 text-white'
                    : 'bg-white/5 text-gray-400 hover:text-white'
                }`}
              >
                全部
              </button>
              {types.map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(filterType === type ? null : type)}
                  className={`px-3 py-1.5 rounded-md text-sm flex items-center gap-1.5 transition-all ${
                    filterType === type
                      ? 'text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                  style={{
                    background: filterType === type
                      ? `${TYPE_COLORS[type]}20`
                      : 'rgba(255, 255, 255, 0.05)',
                    border: filterType === type
                      ? `1px solid ${TYPE_COLORS[type]}50`
                      : '1px solid transparent'
                  }}
                >
                  <div 
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: TYPE_COLORS[type] }}
                  ></div>
                  <span>{TYPE_NAMES[type] || type}</span>
                </button>
              ))}
            </div>
          </div>

          {/* 公司筛选 */}
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-sm">公司:</span>
            <div className="flex flex-wrap gap-1">
              <button
                onClick={() => setFilterCompany(null)}
                className={`px-3 py-1.5 rounded-md text-sm ${
                  !filterCompany
                    ? 'bg-white/20 text-white'
                    : 'bg-white/5 text-gray-400 hover:text-white'
                }`}
              >
                全部
              </button>
              {companies.slice(0, 5).map((company) => (
                <button
                  key={company}
                  onClick={() => setFilterCompany(filterCompany === company ? null : company)}
                  className={`px-3 py-1.5 rounded-md text-sm flex items-center gap-1.5 ${
                    filterCompany === company
                      ? 'text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                  style={{
                    background: filterCompany === company
                      ? `${COMPANY_COLORS[company] || '#6b7280'}20`
                      : 'rgba(255, 255, 255, 0.05)',
                    border: filterCompany === company
                      ? `1px solid ${COMPANY_COLORS[company] || '#6b7280'}50`
                      : '1px solid transparent'
                  }}
                >
                  <div 
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: COMPANY_COLORS[company] || '#6b7280' }}
                  ></div>
                  <span>{company}</span>
                </button>
              ))}
              {companies.length > 5 && (
                <div className="text-gray-500 text-sm px-2">+{companies.length - 5}</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 光子列表 */}
      <div className="flex-1 overflow-y-auto px-2">
        <div className="px-6 py-4">
          {filteredPhotons.length === 0 ? (
            <div className="text-center py-16">
              <div className="text-6xl mb-6 text-gray-700">✨</div>
              <h3 className="text-xl font-bold text-white mb-3">暂无光子</h3>
              <p className="text-gray-400 mb-8">尝试调整筛选条件或添加新的光子</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredPhotons.map((photon) => (
                <div
                  key={photon.id}
                  className="group bg-gradient-to-r from-white/5 to-white/3 rounded-2xl p-6 
                    border border-white/10 hover:border-white/20 transition-all duration-300
                    hover:scale-[1.002] hover:shadow-2xl cursor-pointer"
                >
                  <div className="flex gap-4">
                    {/* 左侧信息 */}
                    <div className="flex-1">
                      {/* 内容 */}
                      <p className="text-lg text-white mb-4 leading-relaxed group-hover:text-gray-100 transition-colors">
                        {photon.content}
                      </p>
                      
                      {/* 元信息 */}
                      <div className="flex flex-wrap items-center gap-4 text-sm">
                        {/* 作者 */}
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 
                            flex items-center justify-center">
                            <span className="text-xs">👤</span>
                          </div>
                          <div>
                            <div className="text-white">{photon.author.split('@')[0]}</div>
                            <div className="text-gray-500 text-xs">{photon.time}</div>
                          </div>
                        </div>
                        
                        {/* 公司 */}
                        <div className="flex items-center gap-2">
                          <div 
                            className="w-8 h-8 rounded-full flex items-center justify-center"
                            style={{ 
                              background: `linear-gradient(135deg, ${COMPANY_COLORS[photon.company] || '#6b7280'}20, transparent)`,
                              border: `1px solid ${COMPANY_COLORS[photon.company] || '#6b7280'}50`
                            }}
                          >
                            <span className="text-xs">🏢</span>
                          </div>
                          <div>
                            <div className="text-white">{photon.company}</div>
                            <div className="text-gray-500 text-xs">{photon.year || '未知年份'}</div>
                          </div>
                        </div>
                        
                        {/* 类型 */}
                        <div className="flex items-center gap-2">
                          <div 
                            className="w-8 h-8 rounded-full flex items-center justify-center"
                            style={{ 
                              background: `linear-gradient(135deg, ${TYPE_COLORS[photon.type] || '#6b7280'}20, transparent)`,
                              border: `1px solid ${TYPE_COLORS[photon.type] || '#6b7280'}50`
                            }}
                          >
                            <span className="text-xs">{getTypeIcon(photon.type)}</span>
                          </div>
                          <div>
                            <div className="text-white">{TYPE_NAMES[photon.type] || photon.type}</div>
                            <div className="text-gray-500 text-xs">类型</div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* 右侧互动 */}
                    <div className="flex flex-col items-end gap-3">
                      {/* 共鸣数 */}
                      <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 
                        group-hover:bg-white/10 transition-colors">
                        <span className="text-lg">💫</span>
                        <span className="font-bold text-white">{photon.likes}</span>
                        <span className="text-gray-400 text-sm">共鸣</span>
                      </div>
                      
                      {/* 互动按钮 */}
                      <div className="flex gap-2">
                        <button className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500/20 to-purple-500/20 
                          text-blue-400 hover:text-white hover:from-blue-500/30 hover:to-purple-500/30 
                          transition-all flex items-center gap-2">
                          <span>💫</span>
                          <span className="text-sm">共鸣</span>
                        </button>
                        
                        <button className="px-4 py-2 rounded-lg bg-white/5 text-gray-400 hover:text-white 
                          hover:bg-white/10 transition-all flex items-center gap-2">
                          <span>💬</span>
                          <span className="text-sm">评论</span>
                        </button>
                        
                        <button className="px-4 py-2 rounded-lg bg-white/5 text-gray-400 hover:text-white 
                          hover:bg-white/10 transition-all">
                          <span>🔗</span>
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  {/* 底部装饰线 */}
                  <div className="mt-6 pt-4 border-t border-white/10 relative">
                    <div 
                      className="absolute top-0 left-0 h-0.5 rounded-full transition-all duration-500 group-hover:w-full"
                      style={{ 
                        width: '60%',
                        background: `linear-gradient(90deg, ${TYPE_COLORS[photon.type] || '#6b7280'}, transparent)`
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* 页脚 */}
      <div className="px-8 py-4 border-t border-white/10">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
              <span>在线</span>
            </div>
            <span>自动刷新: 每 30 秒</span>
          </div>
          <div>
            第 1 页 · 共 {Math.ceil(filteredPhotons.length / 20)} 页
          </div>
        </div>
      </div>
    </div>
  );
}

// 获取类型图标
function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    'moment': '⚡',
    'prophecy': '🔮',
    'culture': '👥',
    'inspiration': '💡',
    'darkmoment': '🕳️',
    'history': '📜',
    'onsite': '📍'
  };
  return icons[type] || '✨';
}
