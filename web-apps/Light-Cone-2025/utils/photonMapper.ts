// utils/photonMapper.ts

export interface StarfieldPhoton {
  id: number | string;
  year: number;
  x: number;
  y: number;
  size: number;
  theme: string;
  color: string;
  title: string;
  character: string;
  company: string;
  description: string;
  resonance: number;
}

// 主题颜色映射
const THEME_COLORS: Record<string, string> = {
  'moment': '#3b82f6',      // 那个瞬间 - 蓝色
  'prophecy': '#8b5cf6',    // 预言胶囊 - 紫色
  'culture': '#f59e0b',     // 行业黑话 - 橙色
  'onsite': '#10b981',      // 我在现场 - 绿色
  'inspiration': '#06b6d4', // 灵光闪现 - 青色
  'history': '#f97316',     // 历史回顾 - 橙色
  'darkmoment': '#ef4444',  // 至暗时刻 - 红色
  // 默认
  'default': '#6b7280'
};

// 公司颜色映射
const COMPANY_COLORS: Record<string, string> = {
  '华为': '#ef4444',
  '蔚来': '#3b82f6',
  '小鹏': '#10b981',
  '特斯拉': '#6b7280',
  '百度': '#3b82f6',
  '理想': '#8b5cf6',
  '其他': '#6b7280'
};

export function mapToStarfieldPhotons(dbPhotons: any[]): StarfieldPhoton[] {
  if (!dbPhotons || dbPhotons.length === 0) {
    return getDefaultPhotons();
  }

  return dbPhotons.map((photon, index) => {
    const theme = photon.type || 'default';
    const company = photon.author_company || '其他';
    
    // 确定颜色：优先使用主题颜色，然后使用公司颜色
    let color = THEME_COLORS[theme] || THEME_COLORS.default;
    
    // 如果有公司颜色且主题是默认的，使用公司颜色
    if (theme === 'default' && COMPANY_COLORS[company]) {
      color = COMPANY_COLORS[company];
    }
    
    // 根据时间分布位置（模拟时间轴）
    const year = getYearFromTimestamp(photon.time);
    const x = calculateXPosition(year, index);
    const y = calculateYPosition(index, dbPhotons.length);
    
    return {
      id: photon.id,
      year: year,
      x: x,
      y: y,
      size: calculateSize(photon.likes || 0),
      theme: theme,
      color: color,
      title: truncateText(photon.content, 50),
      character: photon.author_name || '匿名同行',
      company: company,
      description: photon.content,
      resonance: photon.likes || 0
    };
  });
}

// 辅助函数
function getYearFromTimestamp(timestamp: string): number {
  if (!timestamp) return 2024;
  try {
    const date = new Date(timestamp);
    return date.getFullYear() || 2024;
  } catch {
    return 2024;
  }
}

function calculateXPosition(year: number, index: number): number {
  // 基于年份计算 x 位置 (2015-2035 映射到 15%-85%)
  const minYear = 2015;
  const maxYear = 2035;
  const normalizedYear = Math.min(maxYear, Math.max(minYear, year));
  const baseX = 15 + ((normalizedYear - minYear) / (maxYear - minYear)) * 70;
  
  // 添加一些随机偏移避免重叠
  const randomOffset = (Math.random() - 0.5) * 10;
  return baseX + randomOffset;
}

function calculateYPosition(index: number, total: number): number {
  // 平均分布 y 位置，添加一些随机性
  const baseY = 20 + (index / total) * 60;
  const randomOffset = (Math.random() - 0.5) * 20;
  return baseY + randomOffset;
}

function calculateSize(likes: number): number {
  // 根据点赞数计算大小，最小20，最大40
  return Math.min(40, Math.max(20, 20 + (likes / 10)));
}

function truncateText(text: string, maxLength: number): string {
  if (!text) return '无标题';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

function getDefaultPhotons(): StarfieldPhoton[] {
  // 返回一些示例光子数据
  return [
    {
      id: 1,
      year: 2024,
      x: 50,
      y: 40,
      size: 30,
      theme: 'moment',
      color: '#3b82f6',
      title: '欢迎来到光锥计划',
      character: '系统',
      company: '光锥计划',
      description: '这是一个记录自动驾驶行业声音的平台',
      resonance: 1
    },
    // 可以添加更多示例
  ];
}
