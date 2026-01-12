"use client";

import { useEffect, useRef } from 'react';

interface Star {
  x: number;
  y: number;
  size: number;
  speed: number;
  opacity: number;
  twinkle: number;
  color: string;
}

interface PhotonData {
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

interface StarFieldVisualizationProps {
  photons?: PhotonData[];
  onPhotonClick?: (photon: PhotonData) => void;
  className?: string;
}

const StarFieldVisualization: React.FC<StarFieldVisualizationProps> = ({
  photons = [],
  onPhotonClick,
  className = "",
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationFrameId = useRef<number | null>(null);
  
  // 默认光子数据（如果未提供）
  const defaultPhotonData: PhotonData[] = [
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
    {
      id: 2,
      year: 2023,
      x: 30,
      y: 60,
      size: 25,
      theme: 'prophecy',
      color: '#8b5cf6',
      title: '2023年行业突破',
      character: '行业观察者',
      company: '行业',
      description: '端到端大模型开始应用于自动驾驶系统',
      resonance: 5
    },
    {
      id: 3,
      year: 2025,
      x: 70,
      y: 30,
      size: 35,
      theme: 'inspiration',
      color: '#06b6d4',
      title: '未来的自动驾驶',
      character: '梦想家',
      company: '未来',
      description: '畅想L4级别自动驾驶普及后的生活',
      resonance: 10
    }
  ];

  const displayPhotons = photons.length > 0 ? photons : defaultPhotonData;

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = container.clientWidth;
    let height = container.clientHeight;
    canvas.width = width;
    canvas.height = height;

    // 创建星星
    const stars: Star[] = [];
    const numStars = 300;

    for (let i = 0; i < numStars; i++) {
      stars.push({
        x: Math.random() * width,
        y: Math.random() * height,
        size: Math.random() * 3 + 0.5,
        speed: Math.random() * 0.8 + 0.1,
        opacity: Math.random() * 0.8 + 0.2,
        twinkle: Math.random() * 0.03 + 0.01,
        color: Math.random() > 0.8 ? '#3b82f6' : '#ffffff'
      });
    }

    // 动画循环
    const animate = () => {
      ctx.clearRect(0, 0, width, height);
      
      // 绘制渐变背景
      const gradient = ctx.createRadialGradient(
        width / 2, height / 2, 0,
        width / 2, height / 2, width / 2
      );
      gradient.addColorStop(0, '#0a0a0a');
      gradient.addColorStop(1, '#000000');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);
      
      // 绘制星星
      stars.forEach(star => {
        star.opacity += star.twinkle * (Math.random() > 0.5 ? 1 : -1);
        star.opacity = Math.max(0.1, Math.min(1, star.opacity));
        
        star.x -= star.speed;
        if (star.x < 0) {
          star.x = width;
        }
        
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fillStyle = star.color === '#3b82f6' ? 
          `rgba(59, 130, 246, ${star.opacity})` : 
          `rgba(255, 255, 255, ${star.opacity})`;
        ctx.fill();
        
        // 添加光晕效果
        if (star.size > 1.5) {
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.size * 3, 0, Math.PI * 2);
          ctx.fillStyle = star.color === '#3b82f6' ? 
            `rgba(59, 130, 246, ${star.opacity * 0.1})` : 
            `rgba(255, 255, 255, ${star.opacity * 0.1})`;
          ctx.fill();
        }
      });

      // 绘制光子
      displayPhotons.forEach(photon => {
        const x = (photon.x / 100) * width;
        const y = (photon.y / 100) * height;
        const size = photon.size;
        
        // 绘制光晕
        ctx.beginPath();
        ctx.arc(x, y, size * 2, 0, Math.PI * 2);
        const glowGradient = ctx.createRadialGradient(x, y, 0, x, y, size * 2);
        glowGradient.addColorStop(0, photon.color + '80');
        glowGradient.addColorStop(1, photon.color + '00');
        ctx.fillStyle = glowGradient;
        ctx.fill();
        
        // 绘制光子主体
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        const photonGradient = ctx.createRadialGradient(
          x - size/3, y - size/3, 0,
          x, y, size
        );
        photonGradient.addColorStop(0, '#ffffff');
        photonGradient.addColorStop(0.5, photon.color + 'E0');
        photonGradient.addColorStop(1, photon.color + '80');
        ctx.fillStyle = photonGradient;
        ctx.fill();
        
        // 绘制内发光
        ctx.beginPath();
        ctx.arc(x, y, size * 0.6, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff40';
        ctx.fill();
        
        // 绘制共振数（如果较大）
        if (photon.resonance > 5) {
          ctx.beginPath();
          ctx.arc(x, y, size * 1.5, 0, Math.PI * 2);
          ctx.strokeStyle = photon.color + '30';
          ctx.lineWidth = 2;
          ctx.stroke();
        }
      });
      
      animationFrameId.current = requestAnimationFrame(animate);
    };

    animate();

    // 处理窗口大小变化
    const handleResize = () => {
      width = container.clientWidth;
      height = container.clientHeight;
      canvas.width = width;
      canvas.height = height;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
      window.removeEventListener('resize', handleResize);
    };
  }, [displayPhotons]);

  // 处理点击事件
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !onPhotonClick) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // 检测点击了哪个光子
    let clickedPhoton: PhotonData | null = null;
    let minDistance = Infinity;

    displayPhotons.forEach(photon => {
      const photonX = (photon.x / 100) * canvas.width;
      const photonY = (photon.y / 100) * canvas.height;
      const distance = Math.sqrt((x - photonX) ** 2 + (y - photonY) ** 2);
      
      if (distance < photon.size * 2 && distance < minDistance) {
        minDistance = distance;
        clickedPhoton = photon;
      }
    });
    
    if (clickedPhoton) {
      onPhotonClick(clickedPhoton);
    }
  };

  return (
    <div 
      ref={containerRef} 
      className={`relative w-full h-full ${className}`}
      style={{ background: 'linear-gradient(to bottom, #0a0a0a, #000000)' }}
    >
      <canvas
        ref={canvasRef}
        className="absolute inset-0"
        onClick={handleCanvasClick}
        style={{ cursor: 'pointer' }}
      />
      
      {/* 覆盖层用于显示信息 */}
      <div className="absolute bottom-6 left-6 text-white">
        <div className="bg-black/60 backdrop-blur-lg rounded-xl p-4 border border-blue-500/30">
          <div className="text-sm text-gray-300 mb-2">✨ 星空可视化模式</div>
          <div className="text-xs text-gray-400">点击光子查看详情</div>
        </div>
      </div>
      
      {/* 图例 */}
      <div className="absolute top-6 left-6">
        <div className="bg-black/60 backdrop-blur-lg rounded-xl p-4 border border-blue-500/30 max-w-xs">
          <div className="text-sm font-medium text-gray-300 mb-3">🎨 颜色图例</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span className="text-gray-400">那个瞬间</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-purple-500"></div>
              <span className="text-gray-400">预言胶囊</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-gray-400">我在现场</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-gray-400">至暗时刻</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StarFieldVisualization;
