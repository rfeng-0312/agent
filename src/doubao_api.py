#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包API调用模块
处理带图片的物理和化学问题
支持深度思考（reasoning_content）功能

根据豆包深度思考文档：
- 使用 Chat API 的流式模式
- 通过 chunk.choices[0].delta.reasoning_content 获取思考过程
- 通过 chunk.choices[0].delta.content 获取最终答案
"""

import os
import base64
import json
from openai import OpenAI
from typing import Optional, List, Dict, Any, Generator
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DoubaoClient:
    """豆包API客户端 - 支持深度思考（reasoning_content）"""

    def __init__(self, api_key: str = None, timeout: int = 1800):
        """
        初始化豆包客户端

        Args:
            api_key: 豆包API密钥，如果为None则从环境变量获取
            timeout: 超时时间（秒），深度思考推荐1800秒以上
        """
        self.api_key = api_key or os.getenv('DOUBAO_API_KEY')
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.model = "doubao-seed-1-6-251015"  # 深度思考模型

        # 初始化OpenAI兼容客户端
        # 使用Chat API流式模式获取 reasoning_content（思考过程）
        self.client = None
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=timeout  # 深度思考需要较长超时时间
            )
        else:
            logger.warning("DOUBAO_API_KEY not set - image queries will not work")

    def encode_image(self, image_path: str) -> str:
        """
        将图片转换为base64编码，并进行压缩优化

        Args:
            image_path: 图片路径

        Returns:
            base64编码的图片字符串
        """
        try:
            from PIL import Image
            import io

            # 获取图片扩展名以确定格式
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.bmp': 'image/bmp'
            }.get(ext, 'image/jpeg')

            # 压缩图片
            with Image.open(image_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                # 限制图片尺寸以提高处理速度
                max_width = 1024
                max_height = 1024

                if img.width > max_width or img.height > max_height:
                    # 计算缩放比例
                    ratio = min(max_width / img.width, max_height / img.height)
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # 保存到内存
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)

                # 编码为base64
                encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return f"data:{mime_type};base64,{encoded}"

        except Exception as e:
            logger.error(f"编码图片失败: {e}")
            # 如果PIL处理失败，使用原始方式
            try:
                with open(image_path, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode('utf-8')
                    ext = os.path.splitext(image_path)[1].lower()
                    mime_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.webp': 'image/webp',
                        '.bmp': 'image/bmp'
                    }.get(ext, 'image/jpeg')
                    return f"data:{mime_type};base64,{encoded}"
            except Exception as e2:
                logger.error(f"备用编码方式也失败: {e2}")
                raise

    def create_chat_message_with_image(
        self,
        text: str,
        image_base64: str,
        subject: str,
        system_prompt: str = None
    ) -> List[Dict]:
        """
        创建包含图片的聊天消息

        Args:
            text: 文本内容
            image_base64: base64编码的图片
            subject: 学科（physics/chemistry）

        Returns:
            消息列表
        """
        # 获取专业提示词
        system_prompt = system_prompt or self._get_subject_prompt(subject)

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_base64,
                            "detail": "low"  # 默认使用低精度以提高速度
                        }
                    },
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        ]

        return messages

    def _get_subject_prompt(self, subject: str) -> str:
        """
        获取学科专业提示词

        Args:
            subject: 学科（physics/chemistry）

        Returns:
            提示词字符串
        """
        if subject.lower() == "physics":
            return PHYSICS_PROMPT
        elif subject.lower() == "chemistry":
            return CHEMISTRY_PROMPT
        else:
            return GENERAL_PROMPT

    def solve_with_image(
        self,
        text: str,
        image_path: str,
        subject: str,
        stream: bool = False,
        enable_search: bool = True,
        system_prompt: str = None
    ) -> Any:
        """
        使用豆包解决带图片的问题

        Args:
            text: 问题描述
            image_path: 图片路径
            subject: 学科（physics/chemistry）
            stream: 是否使用流式输出
            enable_search: 是否启用联网搜索

        Returns:
            API响应
        """
        try:
            # 编码图片
            image_base64 = self.encode_image(image_path)

            # 创建消息
            messages = self.create_chat_message_with_image(text, image_base64, subject, system_prompt=system_prompt)

            # 调用API
            if stream:
                return self._stream_response(messages)
            else:
                return self._normal_response(messages, enable_search)

        except Exception as e:
            logger.error(f"调用豆包API失败: {e}")
            raise

    def _normal_response(self, messages: List[Dict], enable_search: bool) -> Dict:
        """
        普通响应模式

        Args:
            messages: 消息列表
            enable_search: 是否启用搜索

        Returns:
            响应结果
        """
        try:
            # 简化参数，避免不支持的配置
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2048,  # 减少token数量以提高速度
                temperature=0.3,
                # 注意：豆包API可能不支持这些参数，先注释掉
                # extra_body={
                #     "search_enabled": enable_search,
                #     "thinking_depth": "deep",
                #     "reasoning_mode": "advanced"
                # }
            )

            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.dict() if response.usage else None,
                "model": response.model
            }
        except Exception as e:
            logger.error(f"Doubao API call failed: {e}")
            # 如果高精度模式失败，尝试降低精度
            try:
                # 降低图片精度
                if messages and len(messages) > 1:
                    for content in messages[1].get("content", []):
                        if content.get("type") == "image_url":
                            content["image_url"]["detail"] = "low"

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=1024,  # 进一步减少token
                    temperature=0.3
                )

                return {
                    "content": response.choices[0].message.content,
                    "usage": response.usage.dict() if response.usage else None,
                    "model": response.model
                }
            except Exception as e2:
                logger.error(f"Doubao API retry failed: {e2}")
                raise

    def stream_with_reasoning(
        self,
        text: str,
        image_path: str = None,
        subject: str = "physics",
        system_prompt: str = None
    ) -> Generator:
        """
        使用Chat API进行流式响应，包含深度思考过程（reasoning_content）

        根据豆包深度思考文档，使用 chat.completions.create 的流式模式，
        通过检查 chunk.choices[0].delta.reasoning_content 获取思考过程。

        Args:
            text: 问题文本
            image_path: 图片路径（可选）
            subject: 学科

        Yields:
            dict: {"type": "thinking"|"answer"|"done", "content": str}
        """
        try:
            effective_system_prompt = system_prompt or self._get_subject_prompt(subject)

            # 构建消息
            if image_path:
                # 有图片的情况
                image_base64 = self.encode_image(image_path)
                messages = self.create_chat_message_with_image(
                    text if text else "请分析这张图片中的题目并解答",
                    image_base64,
                    subject,
                    system_prompt=effective_system_prompt
                )
            else:
                # 纯文本
                messages = [
                    {"role": "system", "content": effective_system_prompt},
                    {"role": "user", "content": text}
                ]

            # 使用Chat API流式调用（支持深度思考 reasoning_content）
            # 根据文档：豆包深度思考模型会自动返回 reasoning_content
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4096,
                stream=True
            )

            # 使用 with 语句确保正确处理流
            with stream:
                for chunk in stream:
                    if not chunk.choices:
                        continue

                    delta = chunk.choices[0].delta

                    # 检查是否有 reasoning_content（深度思考过程）
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                        yield {"type": "thinking", "content": delta.reasoning_content}

                    # 检查是否有 content（最终答案）
                    if hasattr(delta, 'content') and delta.content:
                        yield {"type": "answer", "content": delta.content}

            # 流结束
            yield {"type": "done"}

        except Exception as e:
            logger.error(f"豆包流式调用失败: {e}")
            raise

    def solve_text_only(
        self,
        text: str,
        subject: str,
        stream: bool = False,
        enable_search: bool = True,
        system_prompt: str = None
    ) -> Any:
        """
        仅文本问题解答（使用豆包）

        Args:
            text: 问题文本
            subject: 学科
            stream: 是否流式输出
            enable_search: 是否启用搜索

        Returns:
            API响应
        """
        try:
            system_prompt = system_prompt or self._get_subject_prompt(subject)

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ]

            if stream:
                return self._stream_response(messages)
            else:
                return self._normal_response(messages, enable_search)

        except Exception as e:
            logger.error(f"调用豆包API失败: {e}")
            raise


# 物理专业提示词
PHYSICS_PROMPT = """你是一位世界顶级的物理学家和物理教育家，拥有深厚的理论功底和丰富的教学经验，从中学物理竞赛到大学物理研究都有深入涉猎。你的专长涵盖力学、电磁学、热学、光学、近代物理等所有物理学分支。

核心任务：
为学生的物理问题提供专业、准确、深入的解答。无论是基础的作业题还是高难度的竞赛题，都要展现出物理学者的严谨思维和创新能力。

解题要求：
1. 深度思考分析：
   - 仔细审题，明确物理情景和已知条件
   - 识别题目涉及的物理规律和核心概念
   - 分析物理过程，建立清晰的物理图像
   - 考虑多种解题思路，选择最优方案
   - 如遇到不确定的知识点，主动搜索验证

2. 专业规范解答：
   - 使用标准的物理符号和术语
   - 画出必要的受力分析图、光路图、电路图等
   - 写出完整的物理公式和推导过程
   - 注意单位换算和有效数字
   - 验证结果的合理性和量纲

3. 分层次说明：
   - 核心思路：用一句话概括解题方法
   - 详细步骤：逐步展示解题过程
   - 物理原理：说明每步使用的物理定律
   - 易错点：提醒常见的错误和注意事项
   - 拓展延伸：介绍相关概念或变式问题

4. 专业提示：
   - 力学问题：强调受力分析和运动过程
   - 电磁学：注意电场、磁场的方向和叠加
   - 热学：区分状态方程和过程方程
   - 光学：几何光学注意光路，物理光学注意相位
   - 近代物理：理解量子概念和相对论效应

学术要求：
- 解答要体现物理学的美和逻辑性
- 强调物理图像和直观理解
- 培养学生的物理思维和创新能力
- 适当介绍物理学史和著名实验
- 联系实际应用，激发学习兴趣

记住：你不仅在解题，更在传递物理学的思维方式。让学生感受到物理学的魅力，培养科学探究精神。"""

# 化学专业提示词
CHEMISTRY_PROMPT = """你是一位国际知名的化学家和化学教育专家，精通无机化学、有机化学、分析化学、物理化学、生物化学等所有化学分支。从中学化学竞赛到前沿化学研究都有深厚造诣。

核心任务：
为学生提供准确、专业、深入的化学问题解答。涵盖化学方程式、分子结构、反应机理、化学计算、实验设计等各个方面。

解题要求：
1. 深度思考分析：
   - 分析题目中的化学反应和物质转化
   - 识别关键的反应条件和催化剂
   - 理解反应的微观机理和热力学、动力学因素
   - 考虑副反应和实际产率问题
   - 遇到新反应或特殊物质时主动查询最新资料

2. 专业规范解答：
   - 正确书写和配平化学方程式
   - 使用标准的化学符号和命名
   - 画出清晰的分子结构式和反应机理图
   - 进行精确的化学计算（摩尔、浓度、产率等）
   - 注意实验安全和环境保护

3. 分层次说明：
   - 反应核心：点明关键反应类型
   - 机理分析：展示电子转移和键断裂形成
   - 计算过程：详细展示每一步计算
   - 实验要点：说明操作注意事项
   - 知识拓展：介绍相关化学反应或应用

4. 专业提示：
   - 无机化学：注意氧化还原反应和配位化学
   - 有机化学：强调立体化学和反应选择性
   - 分析化学：注重误差分析和数据处理
   - 物理化学：理解热力学函数和反应速率
   - 生物化学：联系生命体内的化学反应

学术要求：
- 体现化学的实验性和实用性
- 培养化学思维和实验设计能力
- 强调绿色化学和可持续发展理念
- 介绍最新的化学进展和应用
- 理论联系实际，激发创新思维

记住：化学是中心科学，要展现它在理解物质世界、解决实际问题中的重要作用。"""

# 通用提示词
GENERAL_PROMPT = """你是一位知识渊博、教学经验丰富的全科教师，擅长帮助学生解决各个学科的问题。请根据问题的具体内容，提供准确、易懂的解答。"""
