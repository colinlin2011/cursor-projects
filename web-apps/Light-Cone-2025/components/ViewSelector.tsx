// components/ViewSelector.tsx - 完整版
"use client";

interface ViewSelectorProps {
  currentView: 'starfield' | 'list' | 'company';
  onChange: (view: 'starfield' | 'list' | 'company') => void;
}

export default function ViewSelector({ currentView, onChange }: ViewSelectorProps) {
  const views = [
    {
      id: 'starfield' as const,
      name: '星空视图',
      icon: '🌌',
      description: '沉浸式星空探索'
    },
    {
      id: 'list' as const,
      name: '列表视图',
      icon: '📜',
      description: '时间线排列'
    },
    {
      id: 'company' as const,
      name: '公司视图',
      icon: '🏢',
      description: '按公司聚合'
    }
  ];

  return (
    <div className="flex items-center gap-1 p-1 bg-gradient-to-r from-white/5 to-white/3 rounded-xl border border-white/10">
      {views.map((view) => (
        <button
          key={view.id}
          onClick={() => onChange(view.id)}
          className={`relative px-4 py-2 rounded-lg transition-all duration-300 flex items-center gap-2 group ${
            currentView === view.id
              ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white shadow-lg'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
        >
          {/* 选中状态指示器 */}
          {currentView === view.id && (
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg"></div>
          )}
          
          {/* 图标 */}
          <span className="relative z-10 text-lg">{view.icon}</span>
          
          {/* 视图名称 */}
          <span className="relative z-10 font-medium text-sm">{view.name}</span>
          
          {/* 悬停提示 */}
          <div className={`absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1.5 
            bg-gray-900 border border-white/10 rounded-lg text-xs whitespace-nowrap opacity-0 
            group-hover:opacity-100 transition-opacity duration-200 pointer-events-none
            ${currentView === view.id ? 'text-blue-400' : 'text-gray-400'}`}>
            {view.description}
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 
              w-2 h-2 bg-gray-900 border-r border-b border-white/10 rotate-45"></div>
          </div>
          
          {/* 选中状态装饰 */}
          {currentView === view.id && (
            <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-8 h-0.5 
              bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"></div>
          )}
        </button>
      ))}
    </div>
  );
}
