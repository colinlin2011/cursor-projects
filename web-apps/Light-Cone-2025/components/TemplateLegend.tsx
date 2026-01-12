// components/TemplateLegend.tsx - 完整版
"use client";

interface Template {
  id: string;
  name: string;
  description: string;
  color: string;
  icon: string;
}

interface TemplateLegendProps {
  templates: Template[];
  activeTemplate: string | null;
  onTemplateClick: (templateId: string | null) => void;
}

export default function TemplateLegend({ 
  templates, 
  activeTemplate, 
  onTemplateClick 
}: TemplateLegendProps) {
  return (
    <div className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-2xl p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 flex items-center justify-center rounded-lg bg-gradient-to-r from-blue-500/20 to-purple-500/20">
            <span className="text-lg">🎯</span>
          </div>
          <div>
            <h3 className="font-semibold text-white">光子类型</h3>
            <p className="text-xs text-gray-400">点击筛选不同类型的光子</p>
          </div>
        </div>
        
        {activeTemplate && (
          <button
            onClick={() => onTemplateClick(null)}
            className="px-3 py-1.5 text-xs bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
          >
            清除筛选
          </button>
        )}
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-2">
        {templates.map((template) => {
          const isActive = activeTemplate === template.id;
          
          return (
            <button
              key={template.id}
              onClick={() => onTemplateClick(isActive ? null : template.id)}
              className={`relative p-3 rounded-xl transition-all duration-300 group overflow-hidden ${
                isActive 
                  ? 'ring-2 ring-white/30 scale-105' 
                  : 'hover:bg-white/5 hover:scale-102'
              }`}
              style={{
                background: isActive 
                  ? `linear-gradient(135deg, ${template.color}20, ${template.color}10)`
                  : 'transparent'
              }}
            >
              {/* 背景光效 */}
              {isActive && (
                <div 
                  className="absolute inset-0 opacity-30"
                  style={{
                    background: `radial-gradient(circle at center, ${template.color}40, transparent 70%)`
                  }}
                ></div>
              )}
              
              <div className="relative z-10">
                {/* 图标和颜色 */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: template.color }}
                    ></div>
                    <span className="text-lg">{template.icon}</span>
                  </div>
                  
                  {isActive && (
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  )}
                </div>
                
                {/* 名称 */}
                <div className="text-left">
                  <div className={`font-medium text-sm mb-1 ${
                    isActive ? 'text-white' : 'text-gray-300'
                  }`}>
                    {template.name}
                  </div>
                  <div className="text-xs text-gray-500 line-clamp-2">
                    {template.description}
                  </div>
                </div>
              </div>
              
              {/* 悬停效果 */}
              <div className="absolute inset-0 bg-gradient-to-br from-white/0 via-white/0 to-white/5 
                opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </button>
          );
        })}
      </div>
      
      {/* 使用说明 */}
      <div className="mt-4 pt-4 border-t border-white/10">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="text-yellow-500">💡</span>
          <span>不同类型的光子记录了行业的不同声音：瞬间感悟、技术预言、团队故事等</span>
        </div>
      </div>
    </div>
  );
}
