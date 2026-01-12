// components/StarCanvas.tsx - 修复括号错误
"use client";

import { useEffect, useRef, useState, useCallback } from 'react';
import { StarPhoton } from '@/lib/types';

interface StarCanvasProps {
  photons: StarPhoton[];
  timeRange: { start: number; end: number };
  onPhotonClick: (photon: StarPhoton) => void;
  activeCompany?: string | null;
  activeTemplate?: string | null;
}

export default function StarCanvas({ 
  photons = [],
  timeRange = { start: 2015, end: 2035 },
  onPhotonClick,
  activeCompany,
  activeTemplate 
}: StarCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number | null>(null);
  
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [hoveredPhoton, setHoveredPhoton] = useState<StarPhoton | null>(null);
  const startTimeRef = useRef(Date.now());

  // 尺寸自适应
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setDimensions({ width, height });
      }
    };

    updateDimensions();
    const resizeObserver = new ResizeObserver(updateDimensions);
    if (containerRef.current) resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  // 鼠标交互
  const handleMouseMove = useCallback((e: MouseEvent) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    setMousePos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  }, []);

  // 主渲染循环
  useEffect(() => {
    if (!canvasRef.current || dimensions.width === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = dimensions.width * dpr;
    canvas.height = dimensions.height * dpr;
    ctx.scale(dpr, dpr);
    canvas.style.width = `${dimensions.width}px`;
    canvas.style.height = `${dimensions.height}px`;

    const animate = () => {
      const currentTime = Date.now() - startTimeRef.current;
      const width = dimensions.width;
      const height = dimensions.height;

      // 1. 清空画布（半透明拖尾）
      ctx.fillStyle = 'rgba(0, 0, 5, 0.05)';
      ctx.fillRect(0, 0, width, height);

      // 2. 多层星云背景
      drawNebulaBackground(ctx, width, height, currentTime);

      // 3. 深度视差星星
      drawParallaxStars(ctx, width, height, currentTime);

      // 4. 过滤光子
      const filteredPhotons = photons.filter(p => 
        p.year >= timeRange.start && 
        p.year <= timeRange.end &&
        (!activeCompany || p.company === activeCompany) &&
        (!activeTemplate || p.type === activeTemplate)
      );

      // 5. 绘制光子间连接线
      drawPhotonConnections(ctx, filteredPhotons, width, height);

      // 6. 绘制光子（引力透镜效果）
      filteredPhotons.forEach(photon => {
        const x = (photon.x / 100) * width;
        const y = (photon.y / 100) * height;
        
        const distance = Math.sqrt((mousePos.x - x) ** 2 + (mousePos.y - y) ** 2);
        const isHovered = distance < photon.size * 3;
        
        drawGravitationalLens(ctx, x, y, photon, currentTime, isHovered);
      });

      // 7. HUD扫描线
      drawEnhancedScanlines(ctx, width, height, currentTime);

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('click', () => {
      if (hoveredPhoton) onPhotonClick(hoveredPhoton);
    });

    return () => {
      canvas.removeEventListener('mousemove', handleMouseMove);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [dimensions, photons, timeRange, activeCompany, activeTemplate, mousePos, hoveredPhoton]);

  // 渲染悬停卡片
  const renderHoverCard = () => {
    if (!hoveredPhoton) return null;

    const typeNames: Record<string, string> = {
      'moment': '那个瞬间',
      'prophecy': '预言胶囊',
      'culture': '团队文化',
      'inspiration': '灵光闪现',
      'darkmoment': '至暗时刻',
      'history': '历史记录',
      'onsite': '现场观察'
    };

    return (
      <div 
        className="absolute z-20 animate-fade-in"
        style={{ left: mousePos.x + 16, top: mousePos.y - 100 }}
      >
        <div className="bg-black/80 backdrop-blur-xl border border-cyan-500/30 rounded-xl p-4 text-white max-w-xs shadow-2xl">
          <div className="flex items-center gap-2 mb-2">
            <div 
              className="w-3 h-3 rounded-full animate-pulse"
              style={{ backgroundColor: hoveredPhoton.color }}
            ></div>
            <span className="text-xs font-medium" style={{ color: hoveredPhoton.color }}>
              {typeNames[hoveredPhoton.type] || hoveredPhoton.type}
            </span>
            <span className="text-xs text-gray-400">{hoveredPhoton.year}</span>
          </div>
          <p className="text-sm mb-3 line-clamp-3">{hoveredPhoton.content}</p>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-300">{hoveredPhoton.author.split('@')[0]}</span>
            <span className="text-cyan-400 flex items-center gap-1 font-bold">
              💫 {hoveredPhoton.likes}
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div ref={containerRef} className="relative w-full h-full">
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full cursor-crosshair" />
      
      {/* 左上角系统信息 */}
      <div className="absolute top-6 left-6 font-mono text-xs text-cyan-400/60 pointer-events-none">
        <div>LIGHT CONE v2.0</div>
        <div>PHOTONS: {photons.length}</div>
        <div>TIME-RANGE: {timeRange.start}-{timeRange.end}</div>
      </div>

      {/* 时间轴HUD */}
      <div className="absolute bottom-8 left-8 right-8 flex justify-between text-xs text-white/40 font-mono pointer-events-none">
        {[2015, 2020, 2025, 2030, 2035].map(year => (
          <span key={year}>{year}</span>
        ))}
      </div>

      {renderHoverCard()}
    </div>
  );
}

// 多层星云背景
function drawNebulaBackground(ctx: CanvasRenderingContext2D, width: number, height: number, time: number) {
  const nebula1 = ctx.createRadialGradient(width * 0.3, height * 0.2, 0, width * 0.3, height * 0.2, width * 0.6);
  nebula1.addColorStop(0, 'rgba(139, 92, 246, 0.1)');
  nebula1.addColorStop(1, 'rgba(139, 92, 246, 0)');
  ctx.fillStyle = nebula1;
  ctx.fillRect(0, 0, width, height);

  const nebula2 = ctx.createRadialGradient(
    width * 0.7 + Math.sin(time * 0.0001) * 50, 
    height * 0.8 + Math.cos(time * 0.0001) * 30, 
    0, 
    width * 0.7, 
    height * 0.8, 
    width * 0.5
  );
  nebula2.addColorStop(0, 'rgba(6, 182, 212, 0.08)');
  nebula2.addColorStop(1, 'rgba(6, 182, 212, 0)');
  ctx.fillStyle = nebula2;
  ctx.fillRect(0, 0, width, height);
}

// 视差星星（修复括号错误）
function drawParallaxStars(ctx: CanvasRenderingContext2D, width: number, height: number, time: number) {
  const layers = [
    { count: 100, speed: 0.1, size: 0.5, opacity: 0.3 },
    { count: 50, speed: 0.3, size: 1, opacity: 0.6 },
    { count: 25, speed: 0.5, size: 1.5, opacity: 0.9 }
  ];

  layers.forEach((layer, layerIndex) => {
    for (let i = 0; i < layer.count; i++) {
      const seed = i * 1000 + layerIndex * 10000;
      const x = ((Math.sin(seed) * 0.5 + 0.5) * width + time * layer.speed) % width;
      const y = ((Math.cos(seed * 1.5) * 0.5 + 0.5) * height); // ✨ 修复：补全括号
      
      ctx.beginPath();
      ctx.arc(x, y, layer.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${layer.opacity})`;
      ctx.fill();
      
      if (i % 7 === 0) {
        const twinkle = Math.sin(time * 0.003 + seed) * 0.5 + 0.5;
        ctx.beginPath();
        ctx.arc(x, y, layer.size * 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${twinkle * 0.1})`;
        ctx.fill();
      }
    }
  });
}

// 光子连接网络
function drawPhotonConnections(ctx: CanvasRenderingContext2D, photons: StarPhoton[], width: number, height: number) {
  photons.forEach((photon, i) => {
    const x1 = (photon.x / 100) * width;
    const y1 = (photon.y / 100) * height;
    
    photons.slice(i + 1).forEach(otherPhoton => {
      const shouldConnect = otherPhoton.company === photon.company || Math.abs(otherPhoton.year - photon.year) <= 2;
      if (!shouldConnect) return;
      
      const x2 = (otherPhoton.x / 100) * width;
      const y2 = (otherPhoton.y / 100) * height;
      const distance = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
      if (distance > 300) return;
      
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      const alpha = Math.max(0, 1 - distance / 300) * 0.1;
      ctx.strokeStyle = `rgba(6, 182, 212, ${alpha})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    });
  });
}

// 引力透镜效果
function drawGravitationalLens(ctx: CanvasRenderingContext2D, x: number, y: number, photon: StarPhoton, time: number, isHovered: boolean) {
  const fieldRadius = photon.size * 4;
  const fieldGradient = ctx.createRadialGradient(x, y, 0, x, y, fieldRadius);
  fieldGradient.addColorStop(0, `${photon.color}10`);
  fieldGradient.addColorStop(0.5, `${photon.color}05`);
  fieldGradient.addColorStop(1, `${photon.color}00`);
  ctx.fillStyle = fieldGradient;
  ctx.fillRect(x - fieldRadius, y - fieldRadius, fieldRadius * 2, fieldRadius * 2);

  const auraRadius = photon.size * 2 + Math.sin(time * 0.003 + Number(photon.id)) * 5;
  const finalRadius = isHovered ? auraRadius * 1.8 : auraRadius;
  const auraGradient = ctx.createRadialGradient(x, y, 0, x, y, finalRadius);
  auraGradient.addColorStop(0, `${photon.color}60`);
  auraGradient.addColorStop(0.7, `${photon.color}20`);
  auraGradient.addColorStop(1, `${photon.color}00`);
  ctx.fillStyle = auraGradient;
  ctx.fillRect(x - finalRadius, y - finalRadius, finalRadius * 2, finalRadius * 2);

  const coreSize = isHovered ? photon.size * 1.5 : photon.size;
  const coreGradient = ctx.createRadialGradient(x - coreSize/3, y - coreSize/3, 0, x, y, coreSize);
  coreGradient.addColorStop(0, '#ffffff');
  coreGradient.addColorStop(0.6, photon.color);
  coreGradient.addColorStop(1, `${photon.color}80`);
  ctx.fillStyle = coreGradient;
  ctx.beginPath();
  ctx.arc(x, y, coreSize, 0, Math.PI * 2);
  ctx.fill();

  ctx.beginPath();
  ctx.arc(x - coreSize * 0.3, y - coreSize * 0.3, coreSize * 0.25, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
  ctx.fill();

  ctx.beginPath();
  ctx.arc(x, y, coreSize * 1.3, 0, Math.PI * 2);
  ctx.strokeStyle = `${photon.companyColor}80`;
  ctx.lineWidth = 2;
  ctx.shadowBlur = 15;
  ctx.shadowColor = photon.companyColor;
  ctx.stroke();
  ctx.shadowBlur = 0;

  if (photon.likes >= 10) {
    const ringCount = Math.min(4, Math.floor(photon.likes / 15));
    for (let i = 0; i < ringCount; i++) {
      const delay = i * 1200;
      const progress = ((time + delay) % 6000) / 6000;
      const ringRadius = coreSize * 2 + progress * 25;
      const ringAlpha = Math.sin(progress * Math.PI) * 0.6;
      ctx.beginPath();
      ctx.arc(x, y, ringRadius, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(59, 130, 246, ${ringAlpha})`;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  }
}

// 增强HUD扫描线
function drawEnhancedScanlines(ctx: CanvasRenderingContext2D, width: number, height: number, time: number) {
  const scanY = (time * 0.08) % height;
  ctx.fillStyle = `rgba(6, 182, 212, 0.08)`;
  ctx.fillRect(0, scanY - 1, width, 3);
  
  const cornerSize = 25;
  const cornerAlpha = 0.4 + Math.sin(time * 0.002) * 0.2;
  ctx.strokeStyle = `rgba(6, 182, 212, ${cornerAlpha})`;
  ctx.lineWidth = 2;
  
  ctx.beginPath(); ctx.moveTo(0, cornerSize); ctx.lineTo(0, 0); ctx.lineTo(cornerSize, 0); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(width - cornerSize, 0); ctx.lineTo(width, 0); ctx.lineTo(width, cornerSize); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, height - cornerSize); ctx.lineTo(0, height); ctx.lineTo(cornerSize, height); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(width - cornerSize, height); ctx.lineTo(width, height); ctx.lineTo(width, height - cornerSize); ctx.stroke();
}
