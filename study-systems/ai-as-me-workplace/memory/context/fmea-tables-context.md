# FMEA表格缓存上下文记忆

**创建日期**：2026-01-16  
**关联知识**：`knowledge/technical/fmea-tables-cache.md`

---

## 上下文信息

### 数据来源
- **Wiki节点**：https://zyt.feishu.cn/wiki/MdbRwDYNyiv8E8kjWOQcuBvXnef
- **节点类型**：包含系统、算法软件、软件架构、硬件平台相关的FMEA表格
- **组织结构**：4个主要分类（01. 系统、02. 算法软件、03. 软件架构、04. 硬件平台）

### 缓存状态
- **缓存时间**：2026-01-16
- **缓存方式**：递归遍历所有子节点，查找在线表格类型
- **缓存结果**：29个在线表格全部成功缓存

### 应用场景
1. **故障分析**：根据故障模块查询对应FMEA表格
2. **安全分析**：参考FMEA进行安全分析
3. **设计评审**：对照FMEA检查设计完整性
4. **风险评估**：参考FMEA进行风险评估

---

## 关键模块映射

### 软件模块 → FMEA表格

| 模块名称 | FMEA表格 | 记录数 | 重要性 |
|---------|---------|--------|--------|
| Planning | 10_Planning_System_SW_FMEA | 547行 | ⭐⭐⭐ 核心模块 |
| Control | 11_Control_System_SW_FMEA | 465行 | ⭐⭐⭐ 安全关键 |
| EgoMotion | 05_EgoMotion_System_SW_FMEA | 423行 | ⭐⭐ 重要模块 |
| PSD | 07_PSD_System_SW_FMEA | 340行 | ⭐⭐ 重要模块 |
| Calibration | 04_Calibration_System_SW_FMEA | 288行 | ⭐ 一般模块 |
| FreeSpace&OCC | 06_FreeSpace&OCC_System_SW_FMEA | 278行 | ⭐ 一般模块 |
| MOT | 01_MOT_System_SW_FMEA | 278行 | ⭐ 一般模块 |
| Lane&RS | 02_Lane&RS_System_SW_FMEA | 241行 | ⭐ 一般模块 |
| SceneNet | 08_SceneNet_System_SW_FMEA | 196行 | ⭐ 一般模块 |
| ACAM | 09_ACAM_System_SW_FMEA | 190行 | ⭐ 一般模块 |
| TSLR | 03_TSLR_System_SW_FMEA | 147行 | ⭐ 一般模块 |
| Mapper | 12_Mapper_System_SW_FMEA | 146行 | ⭐ 一般模块 |
| Locator | 13_Locator_System_SW_FMEA | 125行 | ⭐ 一般模块 |
| MapService | 14_MapService_System_FMEA | 112行 | ⭐ 一般模块 |

### 硬件平台 → FMEA表格

| 平台名称 | FMEA表格 | 记录数 | 重要性 |
|---------|---------|--------|--------|
| 单8650 ECU | 单8650 ECU HW FMEA | 936行 | ⭐⭐⭐ 主要平台 |
| 5R13V 双8650 | 5R13V 双8650 cECU HW FMEA | 728行 | ⭐⭐⭐ 主要平台 |
| RHP2.0 VH cECU | RHP2.0_VH_cECU_FMEA_Analysis | 497行 | ⭐⭐ 重要平台 |
| 5R7V cECU | 5R7V cECU HW FMEA | 376行 | ⭐⭐ 重要平台 |
| RHP2.0 sCAM | RHP2.0_sCAM_FMEA_Analysis | 214行 | ⭐ 一般平台 |

---

## 快速查询指南

### 按模块查询
- **规划相关**：`10_Planning_System_SW_FMEA`
- **控制相关**：`11_Control_System_SW_FMEA`
- **感知相关**：`01_MOT_System_SW_FMEA`, `02_Lane&RS_System_SW_FMEA`, `06_FreeSpace&OCC_System_SW_FMEA`
- **定位相关**：`12_Mapper_System_SW_FMEA`, `13_Locator_System_SW_FMEA`, `14_MapService_System_FMEA`

### 按平台查询
- **单8650平台**：`单8650 ECU HW FMEA`
- **双8650平台**：`5R13V 双8650 cECU HW FMEA`
- **RHP2.0平台**：`RHP2.0_VH_cECU_FMEA_Analysis`, `RHP2.0_sCAM_FMEA_Analysis`

### 按类型查询
- **Concept FMEA**：`L3 HWP Concept FMEA`, `L4 AVP Concept FMEA`
- **System SW FMEA**：所有`*_System_SW_FMEA`表格
- **HW FMEA**：所有`*_HW_FMEA`表格
- **DFA**：`L2 System DFA`, `RHP2.0_HW DFA_*`

---

## 使用提示

1. **故障分析时**：先确定故障模块，然后查询对应的FMEA表格
2. **安全分析时**：参考Concept FMEA和System SW FMEA
3. **设计评审时**：对照相关模块的FMEA检查设计
4. **风险评估时**：参考FMEA中的失效模式和影响分析

---

**最后更新**：2026-01-16
