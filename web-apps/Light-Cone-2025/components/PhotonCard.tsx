"use client";

import { useState } from 'react';

interface PhotonCardProps {
  photon: {
    id: number | string;
    title: string;
    year: number;
    character: string;
    company: string;
    description: string;
    theme: string;
    resonance: number;
    color: string;
  };
  onResonate?: (id: number | string) => void;
  className?: string;
}

export default function PhotonCard({ photon, onResonate, className = "" }: PhotonCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  // 公司名称映射
  const companyNames: Record<string, string> = {
    'Tesla': '特斯拉',
    'Waymo': 'Waymo',
    'Huawei': '华为',
    'XPeng': '小鹏汽车',
    'LiAuto': '理想汽车',
    'NIO': '蔚来',
    'Xiaomi': '小米',
    'Baidu': '百度',
    'Pony': '小马智行',
    'Momenta': 'Momenta',
    'ZYT': '卓驭',
    'Horizon': '地平线',
    'Mobileye': 'Mobileye',
    'Nvidia': '英伟达',
    'Mercedes': '奔驰',
    'Uber': 'Uber',
    '其他': '其他',
    '华为': '华为',
    '蔚来': '蔚来',
    '小鹏': '小鹏',
    '特斯拉': '特斯拉',
    '百度': '百度',
    '理想': '理想',
    '卓驭': '卓驭'
  };

  // 主题名称映射
  const themeNames: Record<string, string> = {
    'moment': '那个瞬间',
    'prophecy': '预言胶囊',
    'culture': '行业黑话',
    'onsite': '我在现场',
    'inspiration': '灵光闪现',
    'history': '历史回顾',
    'darkmoment': '至暗时刻',
    'default': '其他'
  };

  const displayCompany = companyNames[photon.company] || photon.company;
  const displayTheme = themeNames[photon.theme] || photon.theme;

  return (
    <div 
      className={`bg-black/80 backdrop-blur-xl rounded-xl p-6 border transition-all duration-300 hover:shadow-lg ${className}`}
      style={{ 
        borderColor: `${photon.color}40`,
        boxShadow: isHovered ? `0 0 30px ${photon.color}40` : 'none',
        transform: isHovered ? 'translateY(-4px)' : 'none'
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="text-xl font-bold text-white mb-2">{photon.title}</div>
          <div className="flex items-center gap-3 text-sm">
            <span 
              className="px-2 py-1 rounded-full text-xs font-medium text-white" 
              style={{ backgroundColor: `${photon.color}30` }}
            >
              {displayTheme}
            </span>
            <span className="text-gray-400">{photon.year}年</span>
            <span className="text-gray-400">·</span>
            <span className="text-gray-400">{displayCompany}</span>
          </div>
        </div>
        <button 
          onClick={() => onResonate?.(photon.id)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all hover:scale-105 active:scale-95"
          style={{ backgroundColor: `${photon.color}20`, color: photon.color }}
        >
          <span className="text-lg">💫</span>
          <span className="font-bold">{photon.resonance}</span>
        </button>
      </div>
      
      <div className="mb-4">
        <p className="text-gray-300 leading-relaxed">{photon.description}</p>
      </div>
      
      <div className="flex justify-between items-center pt-4 border-t border-gray-800/50">
        <div className="text-sm text-gray-400">
          <span className="font-medium text-blue-300">{photon.character}</span>
        </div>
        <div className="text-xs text-gray-500">
          光子ID: {typeof photon.id === 'string' ? photon.id.substring(0, 8) + '...' : photon.id}
        </div>
      </div>
    </div>
  );
}
