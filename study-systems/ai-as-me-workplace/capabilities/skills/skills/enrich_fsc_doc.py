# -*- coding: utf-8 -*-
"""
丰富FSC文档内容 - 让文档更专业、完整、详尽

在现有FSC文档基础上，添加更详细和专业的内容
"""

import sys
import os
import time
from typing import Optional, Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_api_wrapper import FeishuAPI

# 配置信息
APP_ID = "cli_a9c92ca516f99bd9"
APP_SECRET = "zlOKnyZkSuSUSr0WlAl6qbh5Qw4eM6wC"
SPACE_ID = "7353073903872868356"
NODE_TOKEN = "DrFAwvNyAi21cJkQj11cUdRZnPh"  # 指定的文档节点token

USER_ACCESS_TOKEN = os.getenv("FEISHU_USER_ACCESS_TOKEN", "u-4tBMNLQZ15Oqb0cGVm.7W.k1n31w4koprGGymw282HUW")

# 详细的FSC内容
DETAILED_FSC_CONTENT = {
    "1. 项目概述": [
        {
            "type": "text",
            "content": "本项目旨在开发舱驾一体域控制器（Cockpit-Drive Integrated Domain Controller），实现座舱域（Cockpit Domain）与驾驶域（Driving Domain）的深度融合，通过统一的硬件平台和软件架构，提供高性能、高可靠性的智能座舱和自动驾驶功能。"
        },
        {
            "type": "heading",
            "level": 4,  # 标题2
            "content": "1.1 项目背景"
        },
        {
            "type": "text",
            "content": "随着汽车电子电气架构从分布式向集中式演进，域控制器成为新一代智能汽车的核心计算单元。舱驾一体域控制器通过整合座舱域和驾驶域的功能，能够："
        },
        {
            "type": "bullet",
            "content": "降低系统成本：减少ECU数量，降低硬件成本和线束复杂度"
        },
        {
            "type": "bullet",
            "content": "提升性能：共享计算资源，实现更高效的资源利用"
        },
        {
            "type": "bullet",
            "content": "增强协同：座舱域和驾驶域可以更好地协同工作，提供更智能的用户体验"
        },
        {
            "type": "bullet",
            "content": "简化架构：统一的硬件平台和软件架构，降低开发和维护复杂度"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "1.2 项目目标"
        },
        {
            "type": "text",
            "content": "本项目的核心目标是开发符合ISO 26262功能安全标准的舱驾一体域控制器，确保系统在提供高性能智能功能的同时，满足汽车功能安全要求。"
        },
        {
            "type": "bullet",
            "content": "功能目标：实现L3级自动驾驶功能和智能座舱交互功能"
        },
        {
            "type": "bullet",
            "content": "安全目标：满足ISO 26262 ASIL-D等级的功能安全要求"
        },
        {
            "type": "bullet",
            "content": "性能目标：支持多路传感器数据融合和实时决策"
        },
        {
            "type": "bullet",
            "content": "可靠性目标：系统可用性≥99.9%，MTBF≥10000小时"
        }
    ],
    "2. 系统边界": [
        {
            "type": "text",
            "content": "系统边界定义了舱驾一体域控制器的功能范围、接口边界和安全责任范围。明确系统边界是进行功能安全分析的基础。"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "2.1 系统功能范围"
        },
        {
            "type": "heading",
            "level": 5,  # 标题3
            "content": "2.1.1 座舱域功能"
        },
        {
            "type": "text",
            "content": "座舱域负责提供人机交互和信息娱乐功能，包括："
        },
        {
            "type": "bullet",
            "content": "信息娱乐系统（IVI）：多媒体播放、导航、语音助手等"
        },
        {
            "type": "bullet",
            "content": "人机交互（HMI）：触摸屏、语音识别、手势识别等"
        },
        {
            "type": "bullet",
            "content": "舒适性控制：空调、座椅、灯光等环境控制"
        },
        {
            "type": "bullet",
            "content": "仪表显示：车辆状态信息显示、告警提示等"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "2.1.2 驾驶域功能"
        },
        {
            "type": "text",
            "content": "驾驶域负责提供辅助驾驶和自动驾驶功能，包括："
        },
        {
            "type": "bullet",
            "content": "环境感知：通过摄像头、雷达、激光雷达等传感器感知周围环境"
        },
        {
            "type": "bullet",
            "content": "决策规划：基于感知结果进行路径规划和行为决策"
        },
        {
            "type": "bullet",
            "content": "车辆控制：控制转向、制动、加速等执行器"
        },
        {
            "type": "bullet",
            "content": "安全监控：实时监控系统状态，确保安全运行"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "2.2 系统接口边界"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "2.2.1 外部接口"
        },
        {
            "type": "text",
            "content": "系统与外部系统的接口包括："
        },
        {
            "type": "bullet",
            "content": "传感器接口：摄像头、毫米波雷达、激光雷达、超声波传感器等"
        },
        {
            "type": "bullet",
            "content": "执行器接口：EPS（电动助力转向）、ESC（电子稳定控制）、EHB（电子液压制动）等"
        },
        {
            "type": "bullet",
            "content": "通信接口：CAN、LIN、以太网、5G/V2X等"
        },
        {
            "type": "bullet",
            "content": "电源接口：12V/48V电源输入、电源管理"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "2.2.2 域间接口"
        },
        {
            "type": "text",
            "content": "座舱域与驾驶域之间的内部接口："
        },
        {
            "type": "bullet",
            "content": "数据共享接口：共享传感器数据、地图数据等"
        },
        {
            "type": "bullet",
            "content": "状态同步接口：同步系统状态、故障信息等"
        },
        {
            "type": "bullet",
            "content": "资源调度接口：共享计算资源、存储资源等"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "2.3 安全责任边界"
        },
        {
            "type": "text",
            "content": "系统对以下安全相关功能负责："
        },
        {
            "type": "bullet",
            "content": "驾驶域功能的安全执行：确保自动驾驶功能的正确性和可靠性"
        },
        {
            "type": "bullet",
            "content": "座舱域对驾驶域的影响控制：防止座舱域功能异常影响驾驶域安全"
        },
        {
            "type": "bullet",
            "content": "域间通信的安全保障：确保域间数据传输的正确性和完整性"
        },
        {
            "type": "bullet",
            "content": "系统故障的安全处理：在系统故障时进入安全状态"
        }
    ],
    "3. 安全目标": [
        {
            "type": "text",
            "content": "安全目标（Safety Goal）是基于危害分析和风险评估（HARA）确定的系统级安全要求。每个安全目标都对应一个具体的危害场景，并定义了系统必须达到的安全水平。"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "3.1 安全目标定义"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SG-1: 防止座舱域功能异常影响驾驶域安全"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-D"
        },
        {
            "type": "text",
            "content": "危害场景：座舱域功能（如信息娱乐系统）发生故障，导致计算资源被占用或系统崩溃，影响驾驶域关键功能的执行，可能导致车辆失控。"
        },
        {
            "type": "text",
            "content": "安全目标：系统应确保座舱域功能的故障不会影响驾驶域关键功能的正常执行，或在检测到影响时及时进入安全状态。"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SG-2: 确保驾驶域关键功能的可用性和可靠性"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-D"
        },
        {
            "type": "text",
            "content": "危害场景：驾驶域关键功能（如环境感知、决策规划、车辆控制）发生故障，导致功能失效或性能下降，可能导致碰撞事故。"
        },
        {
            "type": "text",
            "content": "安全目标：系统应确保驾驶域关键功能在正常运行和故障情况下都能满足功能和安全要求，包括功能冗余、故障检测和降级策略。"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SG-3: 防止域间通信的数据错误和延迟"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-C"
        },
        {
            "type": "text",
            "content": "危害场景：座舱域与驾驶域之间的数据传输发生错误或延迟，导致驾驶域基于错误数据做出决策，或错过关键信息，可能导致不安全行为。"
        },
        {
            "type": "text",
            "content": "安全目标：系统应确保域间通信的数据完整性、正确性和实时性，包括数据校验、超时检测和错误处理机制。"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SG-4: 确保系统在故障情况下的安全状态"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-D"
        },
        {
            "type": "text",
            "content": "危害场景：系统检测到严重故障，但未能及时进入安全状态，继续以不安全的方式运行，可能导致事故。"
        },
        {
            "type": "text",
            "content": "安全目标：系统应在检测到安全相关故障时，在指定的时间内进入预定义的安全状态，并保持在该状态直到故障被清除。"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "3.2 安全目标属性"
        },
        {
            "type": "text",
            "content": "每个安全目标都定义了以下属性："
        },
        {
            "type": "bullet",
            "content": "ASIL等级：从QM到ASIL-D，表示安全完整性等级"
        },
        {
            "type": "bullet",
            "content": "故障容错时间（FTTI）：从故障发生到进入安全状态的最大允许时间"
        },
        {
            "type": "bullet",
            "content": "安全状态：系统在故障情况下应进入的状态（如降级模式、最小风险状态等）"
        },
        {
            "type": "bullet",
            "content": "操作模式：安全目标适用的操作模式（如自动驾驶模式、辅助驾驶模式等）"
        }
    ],
    "4. 功能安全概念": [
        {
            "type": "text",
            "content": "功能安全概念（Functional Safety Concept）描述了如何通过系统设计实现安全目标。它定义了系统架构、安全机制、故障处理策略等，是连接安全目标和系统设计的桥梁。"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "4.1 系统架构设计"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "4.1.1 域隔离架构"
        },
        {
            "type": "text",
            "content": "系统采用物理和逻辑双重隔离的架构设计："
        },
        {
            "type": "bullet",
            "content": "物理隔离：座舱域和驾驶域使用独立的计算单元（SoC），确保硬件层面的隔离"
        },
        {
            "type": "bullet",
            "content": "逻辑隔离：通过虚拟化和容器技术，在软件层面实现域间隔离"
        },
        {
            "type": "bullet",
            "content": "资源隔离：独立的存储、内存和网络资源，防止资源竞争和干扰"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "4.1.2 冗余设计"
        },
        {
            "type": "text",
            "content": "对于ASIL-D的关键功能，采用冗余设计："
        },
        {
            "type": "bullet",
            "content": "传感器冗余：多传感器融合，提高感知可靠性"
        },
        {
            "type": "bullet",
            "content": "计算冗余：关键算法在主备计算单元上并行运行，结果交叉验证"
        },
        {
            "type": "bullet",
            "content": "执行器冗余：关键控制指令通过多个执行器通道输出，确保执行可靠性"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "4.2 安全监控机制"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "4.2.1 运行时监控"
        },
        {
            "type": "text",
            "content": "系统实时监控以下关键指标："
        },
        {
            "type": "bullet",
            "content": "功能执行状态：监控关键功能的执行状态和结果"
        },
        {
            "type": "bullet",
            "content": "资源使用情况：监控CPU、内存、存储等资源的使用情况"
        },
        {
            "type": "bullet",
            "content": "通信状态：监控域间和外部通信的状态和质量"
        },
        {
            "type": "bullet",
            "content": "系统健康状态：监控系统温度、电压等物理参数"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "4.2.2 异常检测"
        },
        {
            "type": "text",
            "content": "系统通过以下方式检测异常："
        },
        {
            "type": "bullet",
            "content": "数据合理性检查：检查传感器数据、计算结果等的合理性"
        },
        {
            "type": "bullet",
            "content": "时序检查：检查功能执行的时序是否符合预期"
        },
        {
            "type": "bullet",
            "content": "一致性检查：检查冗余通道之间的一致性"
        },
        {
            "type": "bullet",
            "content": "边界检查：检查系统参数是否在允许范围内"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "4.3 故障处理策略"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "4.3.1 故障检测"
        },
        {
            "type": "text",
            "content": "系统通过以下机制检测故障："
        },
        {
            "type": "bullet",
            "content": "硬件自检：系统启动时和运行中定期进行硬件自检"
        },
        {
            "type": "bullet",
            "content": "软件监控：通过看门狗、心跳检测等机制监控软件运行状态"
        },
        {
            "type": "bullet",
            "content": "功能测试：定期执行功能测试，验证功能正确性"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "4.3.2 故障诊断"
        },
        {
            "type": "text",
            "content": "系统对检测到的故障进行诊断："
        },
        {
            "type": "bullet",
            "content": "故障分类：根据故障类型、严重程度等进行分类"
        },
        {
            "type": "bullet",
            "content": "故障定位：确定故障发生的具体位置和原因"
        },
        {
            "type": "bullet",
            "content": "故障记录：记录故障信息，用于后续分析和改进"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "4.3.3 故障恢复"
        },
        {
            "type": "text",
            "content": "系统根据故障类型采取不同的恢复策略："
        },
        {
            "type": "bullet",
            "content": "自动恢复：对于临时性故障，系统尝试自动恢复"
        },
        {
            "type": "bullet",
            "content": "降级运行：对于部分功能故障，系统进入降级模式，保留基本功能"
        },
        {
            "type": "bullet",
            "content": "安全停车：对于严重故障，系统进入最小风险状态，安全停车"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "4.4 降级策略"
        },
        {
            "type": "text",
            "content": "系统定义了多级降级策略："
        },
        {
            "type": "bullet",
            "content": "Level 1（轻微降级）：部分非关键功能失效，系统继续正常运行"
        },
        {
            "type": "bullet",
            "content": "Level 2（中度降级）：部分关键功能失效，系统进入受限模式"
        },
        {
            "type": "bullet",
            "content": "Level 3（严重降级）：多个关键功能失效，系统进入最小风险状态"
        },
        {
            "type": "bullet",
            "content": "Level 4（紧急停车）：系统无法保证安全，立即安全停车"
        }
    ],
    "5. 安全机制": [
        {
            "type": "text",
            "content": "安全机制（Safety Mechanism）是实现功能安全概念的具体技术手段。系统采用多层次、多维度的安全机制，确保在各种故障情况下都能保证系统安全。"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "5.1 硬件安全机制"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.1.1 冗余设计"
        },
        {
            "type": "text",
            "content": "关键硬件采用冗余设计："
        },
        {
            "type": "bullet",
            "content": "双SoC架构：座舱域和驾驶域各使用独立的SoC，互不干扰"
        },
        {
            "type": "bullet",
            "content": "冗余电源：双路电源输入，确保电源可靠性"
        },
        {
            "type": "bullet",
            "content": "冗余通信：关键通信通道采用冗余设计"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.1.2 看门狗机制"
        },
        {
            "type": "text",
            "content": "系统采用硬件看门狗和软件看门狗双重保护："
        },
        {
            "type": "bullet",
            "content": "硬件看门狗：独立硬件看门狗芯片，监控系统运行状态"
        },
        {
            "type": "bullet",
            "content": "软件看门狗：应用层看门狗，监控关键任务执行"
        },
        {
            "type": "bullet",
            "content": "多级看门狗：不同层级设置看门狗，提高监控覆盖率"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.1.3 电源监控"
        },
        {
            "type": "text",
            "content": "系统实时监控电源状态："
        },
        {
            "type": "bullet",
            "content": "电压监控：监控各电源轨的电压，检测过压、欠压等异常"
        },
        {
            "type": "bullet",
            "content": "电流监控：监控系统功耗，检测过流等异常"
        },
        {
            "type": "bullet",
            "content": "温度监控：监控系统温度，防止过热"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "5.2 软件安全机制"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.2.1 运行时监控"
        },
        {
            "type": "text",
            "content": "软件层实现全面的运行时监控："
        },
        {
            "type": "bullet",
            "content": "任务监控：监控关键任务的执行时间和执行结果"
        },
        {
            "type": "bullet",
            "content": "资源监控：监控CPU、内存、存储等资源使用情况"
        },
        {
            "type": "bullet",
            "content": "数据监控：监控关键数据的有效性和合理性"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.2.2 数据校验"
        },
        {
            "type": "text",
            "content": "系统对关键数据进行多重校验："
        },
        {
            "type": "bullet",
            "content": "CRC校验：对通信数据进行CRC校验，确保数据完整性"
        },
        {
            "type": "bullet",
            "content": "合理性检查：检查数据的合理性和有效性"
        },
        {
            "type": "bullet",
            "content": "范围检查：检查数据是否在允许范围内"
        },
        {
            "type": "bullet",
            "content": "一致性检查：检查冗余数据之间的一致性"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.2.3 状态机保护"
        },
        {
            "type": "text",
            "content": "系统使用状态机管理关键功能，并实施保护机制："
        },
        {
            "type": "bullet",
            "content": "状态转换检查：检查状态转换的合法性"
        },
        {
            "type": "bullet",
            "content": "状态一致性：确保状态机状态与实际系统状态一致"
        },
        {
            "type": "bullet",
            "content": "异常状态处理：检测和处理异常状态"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "5.3 通信安全机制"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.3.1 数据完整性保护"
        },
        {
            "type": "text",
            "content": "域间和外部通信采用多重数据完整性保护："
        },
        {
            "type": "bullet",
            "content": "CRC校验：对所有通信数据添加CRC校验码"
        },
        {
            "type": "bullet",
            "content": "序列号检查：检查数据包的序列号，检测丢包和乱序"
        },
        {
            "type": "bullet",
            "content": "时间戳验证：验证数据的时间戳，检测延迟和过期数据"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.3.2 超时检测"
        },
        {
            "type": "text",
            "content": "系统对关键通信实施超时检测："
        },
        {
            "type": "bullet",
            "content": "接收超时：检测数据接收超时，及时发现通信故障"
        },
        {
            "type": "bullet",
            "content": "响应超时：检测命令响应超时，及时发现功能故障"
        },
        {
            "type": "bullet",
            "content": "心跳超时：检测心跳信号超时，及时发现系统故障"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "5.4 诊断机制"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.4.1 自检机制"
        },
        {
            "type": "text",
            "content": "系统在启动和运行中执行自检："
        },
        {
            "type": "bullet",
            "content": "启动自检：系统启动时执行全面的硬件和软件自检"
        },
        {
            "type": "bullet",
            "content": "周期性自检：运行中定期执行自检，检测潜在故障"
        },
        {
            "type": "bullet",
            "content": "按需自检：根据需求触发自检，验证系统状态"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.4.2 故障记录"
        },
        {
            "type": "text",
            "content": "系统记录所有安全相关事件："
        },
        {
            "type": "bullet",
            "content": "故障日志：记录故障类型、时间、位置等信息"
        },
        {
            "type": "bullet",
            "content": "事件日志：记录系统状态变化、操作事件等"
        },
        {
            "type": "bullet",
            "content": "诊断数据：记录诊断测试结果、系统参数等"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "5.4.3 故障恢复"
        },
        {
            "type": "text",
            "content": "系统支持多种故障恢复方式："
        },
        {
            "type": "bullet",
            "content": "自动恢复：对于临时性故障，系统自动尝试恢复"
        },
        {
            "type": "bullet",
            "content": "重启恢复：通过系统重启恢复软件故障"
        },
        {
            "type": "bullet",
            "content": "降级恢复：通过功能降级恢复部分功能"
        }
    ],
    "6. 安全需求": [
        {
            "type": "text",
            "content": "安全需求（Safety Requirement）是基于安全目标和功能安全概念导出的系统级和软件级安全要求。安全需求定义了系统必须满足的具体技术指标和实现要求。"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "6.1 系统级安全需求"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SR-1: 系统应实现座舱域与驾驶域的物理隔离"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-D"
        },
        {
            "type": "text",
            "content": "需求描述："
        },
        {
            "type": "bullet",
            "content": "座舱域和驾驶域应使用独立的计算单元（SoC），确保硬件层面的物理隔离"
        },
        {
            "type": "bullet",
            "content": "域间通信应通过专用的安全通信通道，并实施访问控制"
        },
        {
            "type": "bullet",
            "content": "座舱域故障不应影响驾驶域的计算资源和执行环境"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SR-2: 系统应监控关键功能的执行状态"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-D"
        },
        {
            "type": "text",
            "content": "需求描述："
        },
        {
            "type": "bullet",
            "content": "系统应实时监控驾驶域关键功能的执行状态，包括环境感知、决策规划、车辆控制等"
        },
        {
            "type": "bullet",
            "content": "监控周期应≤100ms，确保及时发现功能异常"
        },
        {
            "type": "bullet",
            "content": "监控结果应实时反馈给安全监控模块，触发相应的安全响应"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SR-3: 系统应在检测到故障时进入安全状态"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-D"
        },
        {
            "type": "text",
            "content": "需求描述："
        },
        {
            "type": "bullet",
            "content": "系统应在检测到安全相关故障后，在FTTI（故障容错时间）内进入预定义的安全状态"
        },
        {
            "type": "bullet",
            "content": "对于ASIL-D功能，FTTI应≤200ms"
        },
        {
            "type": "bullet",
            "content": "安全状态应保持稳定，直到故障被清除或系统重启"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SR-4: 系统应记录所有安全相关事件"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-C"
        },
        {
            "type": "text",
            "content": "需求描述："
        },
        {
            "type": "bullet",
            "content": "系统应记录所有安全相关故障、事件和状态变化"
        },
        {
            "type": "bullet",
            "content": "记录应包含时间戳、事件类型、严重程度等完整信息"
        },
        {
            "type": "bullet",
            "content": "记录应持久化存储，支持后续分析和追溯"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SR-5: 系统应支持故障诊断和恢复"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-C"
        },
        {
            "type": "text",
            "content": "需求描述："
        },
        {
            "type": "bullet",
            "content": "系统应能够诊断故障类型和位置，支持故障定位和分析"
        },
        {
            "type": "bullet",
            "content": "系统应支持自动恢复和手动恢复两种方式"
        },
        {
            "type": "bullet",
            "content": "恢复过程应确保系统安全，避免在恢复过程中产生新的风险"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "6.2 软件级安全需求"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SW-SR-1: 软件应实现域间通信的数据校验"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-C"
        },
        {
            "type": "text",
            "content": "需求描述：所有域间通信数据应添加CRC校验码，接收方应验证校验码，检测到校验失败时应丢弃数据并记录错误。"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SW-SR-2: 软件应实现看门狗喂狗机制"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-D"
        },
        {
            "type": "text",
            "content": "需求描述：关键任务应定期喂狗，喂狗周期应≤500ms，超时未喂狗应触发系统复位或进入安全状态。"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "SW-SR-3: 软件应实现资源监控和限制"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-C"
        },
        {
            "type": "text",
            "content": "需求描述：系统应监控CPU、内存等资源使用情况，当资源使用超过阈值时应触发告警或降级策略。"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "6.3 硬件级安全需求"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "HW-SR-1: 硬件应提供独立的看门狗电路"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-D"
        },
        {
            "type": "text",
            "content": "需求描述：系统应配置独立的硬件看门狗芯片，看门狗超时时间应可配置，超时应触发系统复位。"
        },
        {
            "type": "heading",
            "level": 5,
            "content": "HW-SR-2: 硬件应提供电源监控电路"
        },
        {
            "type": "text",
            "content": "ASIL等级：ASIL-C"
        },
        {
            "type": "text",
            "content": "需求描述：系统应配置电源监控电路，实时监控各电源轨电压，检测到过压、欠压等异常时应触发告警。"
        },
        {
            "type": "heading",
            "level": 4,
            "content": "6.4 安全需求验证"
        },
        {
            "type": "text",
            "content": "所有安全需求都应通过以下方式验证："
        },
        {
            "type": "bullet",
            "content": "需求评审：通过需求评审确保需求的完整性和正确性"
        },
        {
            "type": "bullet",
            "content": "设计验证：通过设计评审和仿真验证设计满足需求"
        },
        {
            "type": "bullet",
            "content": "测试验证：通过单元测试、集成测试、系统测试验证实现满足需求"
        },
        {
            "type": "bullet",
            "content": "安全分析：通过FTA、FMEA等安全分析方法验证需求的有效性"
        }
    ]
}

def create_text_block(content: str) -> dict:
    """创建文本块"""
    return {
        "block_type": 2,
        "text": {
            "elements": [
                {
                    "text_run": {
                        "content": content
                    }
                }
            ]
        }
    }

def create_heading_block(title: str, level: int = 4) -> dict:
    """创建标题块"""
    heading_fields = {
        3: "heading1",
        4: "heading2",
        5: "heading3",
        6: "heading4",
        7: "heading5"
    }
    field_name = heading_fields.get(level, "heading2")
    
    return {
        "block_type": level,
        field_name: {
            "elements": [
                {
                    "text_run": {
                        "content": title
                    }
                }
            ]
        }
    }

def create_bullet_block(content: str) -> dict:
    """创建无序列表块"""
    return {
        "block_type": 12,
        "bullet": {
            "elements": [
                {
                    "text_run": {
                        "content": content
                    }
                }
            ]
        }
    }

def get_document_id_from_node(api: FeishuAPI, space_id: str, node_token: str) -> Optional[str]:
    """从节点获取document_id"""
    result = api.get_wiki_node(space_id, node_token, use_user_token=True)
    
    if result:
        # Wiki v2 API可能直接返回节点信息，也可能在node字段中
        node = result.get('node', result) if 'node' in result else result
        obj_token = node.get('obj_token')
        obj_type = node.get('obj_type')
        
        if obj_type == 'docx' and obj_token:
            return obj_token
    
    return None

def add_content_to_section(api: FeishuAPI, document_id: str, section_title: str, contents: list):
    """向指定章节添加内容"""
    print(f"  丰富章节: {section_title}")
    
    for content_item in contents:
        if content_item['type'] == 'text':
            block = create_text_block(content_item['content'])
        elif content_item['type'] == 'heading':
            block = create_heading_block(content_item['content'], content_item.get('level', 4))
        elif content_item['type'] == 'bullet':
            block = create_bullet_block(content_item['content'])
        else:
            continue
        
        result = api.create_block(
            document_id=document_id,
            block_id=document_id,
            children=[block],
            document_revision_id=-1,
            use_user_token=True
        )
        
        if result:
            print(f"    [OK] 添加: {content_item['content'][:50]}...")
        else:
            print(f"    [X] 添加失败: {content_item['content'][:50]}...")
        
        time.sleep(0.3)  # 避免频率限制

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print("丰富FSC文档内容")
    print("=" * 60)
    print()
    
    if not USER_ACCESS_TOKEN:
        print("[X] 错误：未设置USER_ACCESS_TOKEN")
        return
    
    # 初始化API
    api = FeishuAPI(
        plugin_id="",
        plugin_secret="",
        app_id=APP_ID,
        app_secret=APP_SECRET
    )
    api.set_user_access_token(USER_ACCESS_TOKEN)
    
    # 获取document_id
    print("步骤1：获取文档ID...")
    document_id = get_document_id_from_node(api, SPACE_ID, NODE_TOKEN)
    
    if not document_id:
        print("[X] 无法获取document_id")
        return
    
    print(f"[OK] 文档ID: {document_id}")
    print()
    
    # 添加详细内容
    print("步骤2：添加详细内容...")
    print()
    
    for section_title, contents in DETAILED_FSC_CONTENT.items():
        add_content_to_section(api, document_id, section_title, contents)
        print()
    
    print("=" * 60)
    print("[OK] 内容添加完成！")
    print("=" * 60)
    print()
    print(f"文档节点token: {NODE_TOKEN}")
    print(f"文档ID: {document_id}")
    print(f"文档链接: https://bytedance.larkoffice.com/wiki/{SPACE_ID}/{NODE_TOKEN}")

if __name__ == "__main__":
    main()
