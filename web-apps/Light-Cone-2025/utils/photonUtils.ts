// utils/photonUtils.ts - 修复版
import { Photon, PhotonFromDB } from '@/lib/types';

// 将 PhotonFromDB 转换为前端 Photon 类型
export function photonMapper(dbPhoton: PhotonFromDB): Photon {
  return {
    id: dbPhoton.id,
    content: dbPhoton.content,
    type: dbPhoton.template_type,
    author: dbPhoton.author_name,
    author_name: dbPhoton.author_name,
    author_company: dbPhoton.author_company,
    author_profession: dbPhoton.author_profession,
    likes: dbPhoton.likes_count,
    time: dbPhoton.created_at,
    company: dbPhoton.author_company || '其他',
    isFromDB: true,
    // 移除 created_at，因为它不在 Photon 类型定义中
    // 创建时间已通过 time 字段传递
  };
}

// 根据光子类型获取颜色
export function getPhotonColor(type: string): string {
  const colors: Record<string, string> = {
    'moment': '#3b82f6',
    'prophecy': '#8b5cf6',
    'culture': '#f59e0b',
    'inspiration': '#06b6d4',
    'darkmoment': '#ef4444',
    'history': '#f97316',
    'onsite': '#10b981'
  };
  return colors[type] || '#6b7280';
}
