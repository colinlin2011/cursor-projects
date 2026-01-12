// components/CompanyView.tsx - 完整版
"use client";

import { useState, useMemo } from 'react';
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

interface CompanyViewProps {
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

export default function CompanyView({ photons }: CompanyViewProps) {
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'photons' | 'likes' | 'name'>('photons');
  const [yearRange, setYearRange] = useState<[number, number]>([2015, 2035]);

  // 按公司聚合数据
  const companyStats = useMemo(() => {
    const stats: Record<string, {
      name: string;
      photonCount: number;
      totalLikes: number;
      avgLikes: number;
      types: Record<string, number>;
      years: Record<number, number>;
      photons: Photon[];
      color: string;
    }> = {};

    // 初始化所有公司
    Object.keys(COMPANY_COLORS).forEach(company => {
      stats[company] = {
        name: company,
        photonCount: 0,
        totalLikes: 0,
        avgLikes: 0,
        types: {},
        years: {},
        photons: [],
        color: COMPANY_COLORS[company]
      };
    });

    // 统计其他公司
    stats['其他'] = {
      name: '其他',
      photonCount: 0,
      totalLikes: 0,
      avgLikes: 0,
      types: {},
      years: {},
      photons: [],
      color: '#6b7280'
    };

    // 计算统计数据
    photons.forEach(photon => {
      const company = photon.company in COMPANY_COLORS ? photon.company : '其他';
      const stat = stats[company];
      
      stat.photonCount++;
      stat.totalLikes += photon.likes;
      stat.photons.push(photon);
      
      // 统计类型分布
      stat.types[photon.type] = (stat.types[photon.type] || 0) + 1;
      
      // 统计年份分布
      if (photon.year) {
        stat.years[photon.year] = (stat.years[photon.year] || 0) + 1;
      }
    });

    // 计算平均共鸣数
    Object.values(stats).forEach(stat => {
      stat.avgLikes = stat.photonCount > 0 ? Math.round(stat.totalLikes / stat.photonCount) : 0;
    });

    return stats;
  }, [photons]);

  // 获取公司列表（排序）
  const companies = useMemo(() => {
    return Object.values(companyStats)
      .filter(company => company.photonCount > 0)
      .sort((a, b) => {
        switch (sortBy) {
          case 'photons':
            return b.photonCount - a.photonCount;
          case 'likes':
            return b.totalLikes - a.totalLikes;
          case 'name':
            return a.name.localeCompare(b.name);
          default:
            return 0;
        }
      });
  }, [companyStats, sortBy]);

  // 获取选中的公司数据
  const selectedCompanyData = selectedCompany ? companyStats[selectedCompany] : null;
  
  // 获取年份过滤后的光子
  const filteredPhotons = selectedCompanyData 
    ? selectedCompanyData.photons.filter(p => 
        (!p.year || (p.year >= yearRange[0] && p.year <= yearRange[1]))
      )
    : [];

  return (
    <div className="h-full flex">
      {/* 左侧公司列表 */}
      <div className="w-80 border-r border-white/10 flex flex-col">
        {/* 标题 */}
        <div className="px-6 py-4 border-b border-white/10">
          <h2 className="text-xl font-bold text-white">公司聚合</h2>
          <p className="text-gray-400 text-sm mt-1">按公司查看光子分布</p>
        </div>

        {/* 控制栏 */}
        <div className="px-4 py-3 border-b border-white/10 bg-gradient-to-r from-white/5 to-transparent">
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">排序:</span>
            <div className="flex bg-white/5 rounded-lg p-1">
              {[
                { id: 'photons', label: '光子数', icon: '✨' },
                { id: 'likes', label: '共鸣数', icon: '💫' },
                { id: 'name', label: '名称', icon: '🏢' }
              ].map((option) => (
                <button
                  key={option.id}
                  onClick={() => setSortBy(option.id as any)}
                  className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
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
        </div>

        {/* 公司列表 */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-3 space-y-2">
            {companies.map((company) => {
              const isSelected = selectedCompany === company.name;
              
              return (
                <button
                  key={company.name}
                  onClick={() => setSelectedCompany(isSelected ? null : company.name)}
                  className={`w-full p-4 rounded-xl transition-all duration-300 text-left group ${
                    isSelected
                      ? 'ring-2 ring-white/30 scale-[1.02]'
                      : 'hover:scale-[1.01]'
                  }`}
                  style={{
                    background: isSelected
                      ? `linear-gradient(135deg, ${company.color}20, ${company.color}10)`
                      : 'linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01))',
                    border: `1px solid ${company.color}${isSelected ? '50' : '10'}`
                  }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div 
                        className="w-10 h-10 rounded-lg flex items-center justify-center"
                        style={{
                          background: `linear-gradient(135deg, ${company.color}30, ${company.color}10)`,
                          border: `1px solid ${company.color}50`
                        }}
                      >
                        <span className="text-lg">🏢</span>
                      </div>
                      <div>
                        <div className="font-bold text-white">{company.name}</div>
                        <div className="text-xs text-gray-400 mt-1">
                          {company.photonCount} 个光子
                        </div>
                      </div>
                    </div>
                    
                    {isSelected && (
                      <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                    )}
                  </div>

                  {/* 数据统计 */}
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="p-2 rounded-lg bg-white/5">
                      <div className="text-gray-400 text-xs">总共鸣</div>
                      <div className="text-white font-bold flex items-center gap-1">
                        <span>💫</span>
                        <span>{company.totalLikes}</span>
                      </div>
                    </div>
                    
                    <div className="p-2 rounded-lg bg-white/5">
                      <div className="text-gray-400 text-xs">平均共鸣</div>
                      <div className="text-white font-bold">{company.avgLikes}</div>
                    </div>
                  </div>

                  {/* 类型分布预览 */}
                  <div className="mt-3">
                    <div className="text-xs text-gray-400 mb-1">类型分布</div>
                    <div className="flex gap-1">
                      {Object.entries(company.types)
                        .slice(0, 4)
                        .map(([type, count]) => (
                          <div
                            key={type}
                            className="flex-1 h-1.5 rounded-full"
                            style={{
                              backgroundColor: TYPE_COLORS[type] || '#6b7280',
                              opacity: count / Math.max(...Object.values(company.types)) * 0.8 + 0.2
                            }}
                            title={`${TYPE_NAMES[type] || type}: ${count}`}
                          ></div>
                        ))}
                    </div>
                  </div>

                  {/* 悬停效果 */}
                  <div className="absolute inset-0 bg-gradient-to-br from-white/0 via-white/0 to-white/5 
                    opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl"></div>
                </button>
              );
            })}
          </div>
        </div>

        {/* 统计摘要 */}
        <div className="p-4 border-t border-white/10">
          <div className="text-xs text-gray-400 mb-2">全局统计</div>
          <div className="grid grid-cols-3 gap-2">
            <div className="text-center">
              <div className="text-lg font-bold text-white">
                {photons.length}
              </div>
              <div className="text-xs text-gray-400">总光子</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-white">
                {companies.length}
              </div>
              <div className="text-xs text-gray-400">参与公司</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-white">
                {Math.round(photons.reduce((sum, p) => sum + p.likes, 0) / photons.length) || 0}
              </div>
              <div className="text-xs text-gray-400">平均共鸣</div>
            </div>
          </div>
        </div>
      </div>

      {/* 右侧详情 */}
      <div className="flex-1 flex flex-col">
        {selectedCompanyData ? (
          <>
            {/* 公司详情标题 */}
            <div className="px-8 py-6 border-b border-white/10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div 
                    className="w-16 h-16 rounded-2xl flex items-center justify-center"
                    style={{
                      background: `linear-gradient(135deg, ${selectedCompanyData.color}30, ${selectedCompanyData.color}10)`,
                      border: `2px solid ${selectedCompanyData.color}50`
                    }}
                  >
                    <span className="text-3xl">🏢</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">{selectedCompanyData.name}</h2>
                    <p className="text-gray-400 mt-1">
                      {selectedCompanyData.photonCount} 个光子 · 
                      💫 {selectedCompanyData.totalLikes} 共鸣 · 
                      ⭐ {selectedCompanyData.avgLikes} 平均共鸣
                    </p>
                  </div>
                </div>
                
                <button
                  onClick={() => setSelectedCompany(null)}
                  className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                >
                  返回列表
                </button>
              </div>
            </div>

            {/* 数据可视化 */}
            <div className="px-8 py-6 border-b border-white/10">
              <div className="grid grid-cols-2 gap-6">
                {/* 类型分布 */}
                <div className="bg-white/5 rounded-xl p-4">
                  <h3 className="font-semibold text-white mb-4">光子类型分布</h3>
                  <div className="space-y-3">
                    {Object.entries(selectedCompanyData.types)
                      .sort(([,a], [,b]) => b - a)
                      .map(([type, count]) => (
                        <div key={type} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div 
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: TYPE_COLORS[type] || '#6b7280' }}
                            ></div>
                            <span className="text-sm text-gray-300">
                              {TYPE_NAMES[type] || type}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                              <div 
                                className="h-full rounded-full"
                                style={{
                                  width: `${(count / selectedCompanyData.photonCount) * 100}%`,
                                  backgroundColor: TYPE_COLORS[type] || '#6b7280'
                                }}
                              ></div>
                            </div>
                            <span className="text-sm text-white font-medium w-8 text-right">
                              {count}
                            </span>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>

                {/* 年份分布 */}
                <div className="bg-white/5 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-white">时间分布</h3>
                    <div className="text-xs text-gray-400">
                      {yearRange[0]} - {yearRange[1]}
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    {Object.entries(selectedCompanyData.years)
                      .sort(([a], [b]) => parseInt(a) - parseInt(b))
                      .map(([year, count]) => {
                        const yearNum = parseInt(year);
                        const isInRange = yearNum >= yearRange[0] && yearNum <= yearRange[1];
                        
                        return (
                          <div key={year} className="flex items-center justify-between">
                            <span className={`text-sm ${isInRange ? 'text-white' : 'text-gray-500'}`}>
                              {year}
                            </span>
                            <div className="flex items-center gap-2">
                              <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full rounded-full transition-all duration-500 ${
                                    isInRange ? 'opacity-100' : 'opacity-30'
                                  }`}
                                  style={{
                                    width: `${(count / Math.max(...Object.values(selectedCompanyData.years))) * 100}%`,
                                    backgroundColor: selectedCompanyData.color
                                  }}
                                ></div>
                              </div>
                              <span className={`text-sm font-medium w-8 text-right ${
                                isInRange ? 'text-white' : 'text-gray-500'
                              }`}>
                                {count}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                  </div>
                  
                  {/* 年份范围滑块 */}
                  <div className="mt-6">
                    <input
                      type="range"
                      min="2015"
                      max="2035"
                      value={yearRange[0]}
                      onChange={(e) => setYearRange([parseInt(e.target.value), yearRange[1]])}
                      className="w-full h-1 bg-white/10 rounded-full appearance-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white"
                    />
                    <input
                      type="range"
                      min="2015"
                      max="2035"
                      value={yearRange[1]}
                      onChange={(e) => setYearRange([yearRange[0], parseInt(e.target.value)])}
                      className="w-full h-1 bg-white/10 rounded-full appearance-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white mt-2"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* 光子列表 */}
            <div className="flex-1 overflow-y-auto">
              <div className="px-8 py-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-white">
                    光子列表 ({filteredPhotons.length})
                  </h3>
                  <div className="text-sm text-gray-400">
                    筛选: {yearRange[0]} - {yearRange[1]}
                  </div>
                </div>
                
                <div className="space-y-4">
                  {filteredPhotons.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="text-5xl mb-4 text-gray-700">🌌</div>
                      <h4 className="text-lg font-bold text-white mb-2">暂无光子</h4>
                      <p className="text-gray-400">该时间段内没有光子记录</p>
                    </div>
                  ) : (
                    filteredPhotons.map((photon) => (
                      <div
                        key={photon.id}
                        className="group bg-gradient-to-r from-white/5 to-transparent rounded-xl p-4 
                          border border-white/10 hover:border-white/20 transition-all duration-300"
                      >
                        <div className="flex gap-4">
                          {/* 左侧图标 */}
                          <div className="flex-shrink-0">
                            <div 
                              className="w-12 h-12 rounded-xl flex items-center justify-center"
                              style={{
                                background: `linear-gradient(135deg, ${TYPE_COLORS[photon.type] || '#6b7280'}30, transparent)`,
                                border: `1px solid ${TYPE_COLORS[photon.type] || '#6b7280'}50`
                              }}
                            >
                              <span className="text-xl">
                                {getTypeIcon(photon.type)}
                              </span>
                            </div>
                          </div>
                          
                          {/* 内容 */}
                          <div className="flex-1">
                            <p className="text-white mb-3">{photon.content}</p>
                            
                            <div className="flex items-center gap-4 text-sm">
                              <div className="flex items-center gap-2">
                                <span className="text-gray-400">👤</span>
                                <span className="text-gray-300">{photon.author.split('@')[0]}</span>
                              </div>
                              
                              <div className="flex items-center gap-2">
                                <span className="text-gray-400">📅</span>
                                <span className="text-gray-300">{photon.time}</span>
                              </div>
                              
                              <div className="flex items-center gap-2">
                                <span className="text-gray-400">💫</span>
                                <span className="text-gray-300">{photon.likes}</span>
                              </div>
                            </div>
                          </div>
                          
                          {/* 右侧共鸣按钮 */}
                          <button className="self-start px-3 py-1.5 rounded-lg bg-gradient-to-r from-blue-500/20 to-purple-500/20 
                            text-blue-400 hover:text-white hover:from-blue-500/30 hover:to-purple-500/30 
                            transition-all flex items-center gap-1.5">
                            <span>💫</span>
                            <span className="text-sm">共鸣</span>
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </>
        ) : (
          /* 无选中公司时的提示 */
          <div className="flex-1 flex flex-col items-center justify-center">
            <div className="text-center max-w-lg">
              <div className="text-7xl mb-6 animate-pulse">🏢</div>
              <h3 className="text-2xl font-bold text-white mb-4">选择一家公司</h3>
              <p className="text-gray-400 mb-8">
                点击左侧的公司卡片，查看该公司的光子分布、类型统计和时间趋势
              </p>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-400">共 {companies.length} 家公司参与记录</span>
              </div>
            </div>
          </div>
        )}
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
