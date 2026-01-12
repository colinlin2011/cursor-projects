// components/TemplateSelector.tsx - 修复版
"use client";

interface PhotonTemplate {
  id: string;
  name: string;
  description: string;
  color: string;
  icon: string;
  prompt?: string;
}

interface TemplateSelectorProps {
  templates: PhotonTemplate[];
  selectedTemplate: PhotonTemplate;
  onSelect: (template: PhotonTemplate) => void;
}

export default function TemplateSelector({ templates, selectedTemplate, onSelect }: TemplateSelectorProps) {
  // 计算边框颜色（基于背景色调整透明度）
  const getBorderColor = (color: string, isSelected: boolean) => {
    if (isSelected) {
      return color + '80'; // 80% 不透明度
    }
    return color + '30'; // 30% 不透明度
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <span>🎯</span>
          <span>选择光子类型</span>
        </h3>
        <p className="text-gray-400 text-sm">
          不同类型的模板帮助您更好地记录行业声音
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {templates.map((template) => {
          const isSelected = selectedTemplate.id === template.id;
          
          return (
            <button
              key={template.id}
              onClick={() => onSelect(template)}
              className={`relative p-4 rounded-xl transition-all duration-300 group overflow-hidden ${
                isSelected ? 'scale-105' : 'hover:scale-102'
              }`}
              style={{
                background: isSelected
                  ? `linear-gradient(135deg, ${template.color}20, ${template.color}10)`
                  : 'rgba(255, 255, 255, 0.03)',
                border: `1px solid ${getBorderColor(template.color, isSelected)}`
              }}
            >
              {/* 选中状态指示器 */}
              {isSelected && (
                <div 
                  className="absolute inset-0 opacity-20"
                  style={{
                    background: `radial-gradient(circle at center, ${template.color}40, transparent 70%)`
                  }}
                ></div>
              )}

              <div className="relative z-10">
                <div className="flex flex-col items-center gap-2">
                  {/* 图标 */}
                  <div 
                    className="w-12 h-12 rounded-full flex items-center justify-center text-xl"
                    style={{ 
                      backgroundColor: template.color,
                      color: getTextColor(template.color)
                    }}
                  >
                    {template.icon}
                  </div>
                  
                  {/* 名称 */}
                  <div className="text-center">
                    <div className={`font-medium ${isSelected ? 'text-white' : 'text-gray-300'}`}>
                      {template.name}
                    </div>
                    <div className="text-xs text-gray-500 mt-1 line-clamp-2">
                      {template.description}
                    </div>
                  </div>
                </div>
              </div>

              {/* 选中状态标记 */}
              {isSelected && (
                <div className="absolute top-2 right-2">
                  <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                </div>
              )}

              {/* 悬停效果 */}
              <div className="absolute inset-0 bg-gradient-to-br from-white/0 via-white/0 to-white/5 
                opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </button>
          );
        })}
      </div>

      {/* 当前选中的模板提示 */}
      {selectedTemplate.prompt && (
        <div className="mt-4 p-3 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg">
          <div className="flex items-start gap-2">
            <span className="text-blue-400">💡</span>
            <div>
              <div className="text-sm text-blue-400 font-medium">提示</div>
              <div className="text-sm text-gray-400 mt-1">{selectedTemplate.prompt}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// 根据背景色计算文本颜色（浅色背景用深色文字，深色背景用浅色文字）
function getTextColor(backgroundColor: string): string {
  // 如果是简单的颜色名称，返回默认值
  if (!backgroundColor.startsWith('#')) {
    return '#ffffff';
  }
  
  try {
    // 解析十六进制颜色
    const hex = backgroundColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    // 计算相对亮度
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    
    // 根据亮度返回黑色或白色
    return brightness > 128 ? '#000000' : '#ffffff';
  } catch {
    return '#ffffff';
  }
}
