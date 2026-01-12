// components/DatabaseStatus.tsx
import { DbStatus } from '@/lib/types';

interface DatabaseStatusProps {
  status: DbStatus;
  photonCount: number;
}

export default function DatabaseStatus({ status, photonCount }: DatabaseStatusProps) {
  const getStatusContent = () => {
    switch (status) {
      case "checking":
        return { text: "🔄 检查数据库连接...", className: "text-yellow-400" };
      case "connected":
        return { text: `✅ 数据库已连接 | 当前光子数: ${photonCount}`, className: "text-green-400" };
      case "error":
        return { text: "❌ 数据库连接失败 | 使用演示模式", className: "text-red-400" };
    }
  };

  const content = getStatusContent();

  return (
    <div className={`p-3 rounded-lg mb-4 ${
      status === "connected" ? "bg-green-500/20 border border-green-500/30" :
      status === "error" ? "bg-red-500/20 border border-red-500/30" :
      "bg-yellow-500/20 border border-yellow-500/30"
    }`}>
      <div className="flex items-center justify-center">
        <span className={content.className}>{content.text}</span>
      </div>
    </div>
  );
}
