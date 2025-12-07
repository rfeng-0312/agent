# 深度思考工作流实现计划

## 概述

根据用户选择的"深度思考"开关，系统将切换到不同的工作流：
- **关闭（普通模式）**：处理简单问题，单次API调用，快速响应
- **开启（深度思考模式）**：处理竞赛级复杂问题，多次API调用，包含答案验证

## 工作流对比

### 普通模式（现有流程）
```
用户提问 → 单次API调用 → 返回答案
```

### 深度思考模式（新流程）
```
用户提问 → 第一次调用：解答问题 → 第二次调用：验证答案 → 整合输出
```

## 详细设计

### 1. 深度思考工作流结构

```
┌─────────────────────────────────────────────────────────────┐
│                    深度思考工作流                            │
├─────────────────────────────────────────────────────────────┤
│  阶段1: 问题解答 (Solving Phase)                            │
│  ├─ 使用竞赛级专业提示词                                    │
│  ├─ 调用豆包/DeepSeek API                                   │
│  ├─ 获取详细解答过程和答案                                  │
│  └─ 输出: 思考过程 + 初步答案                               │
├─────────────────────────────────────────────────────────────┤
│  阶段2: 答案验证 (Verification Phase)                       │
│  ├─ 构造验证提示词（包含原题+初步答案）                     │
│  ├─ 调用API进行独立验证                                     │
│  ├─ 检查计算过程、逻辑推理、边界条件                        │
│  └─ 输出: 验证结果 + 修正建议（如有）                       │
├─────────────────────────────────────────────────────────────┤
│  阶段3: 结果整合 (Integration Phase)                        │
│  ├─ 如果验证通过: 输出最终答案                              │
│  ├─ 如果发现错误: 显示修正后的答案                          │
│  └─ 附加: 易错点提醒、拓展知识                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. 前端显示设计

结果页面需要支持多阶段显示：

```
┌─────────────────────────────────────────────────────────────┐
│  [折叠] AI思考过程                                          │
│  └─ 第一阶段思考内容...                                     │
├─────────────────────────────────────────────────────────────┤
│  [展开] 初步解答                                            │
│  └─ 详细解题步骤和初步答案                                  │
├─────────────────────────────────────────────────────────────┤
│  [折叠] 答案验证过程                                        │
│  ├─ 验证思考过程...                                         │
│  └─ 验证结论: ✓ 答案正确 / ⚠ 发现问题                      │
├─────────────────────────────────────────────────────────────┤
│  [展开] 最终答案                                            │
│  ├─ 确认/修正后的答案                                       │
│  └─ 易错点提醒                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3. API调用策略

#### 3.1 文本问题（DeepSeek）
```python
# 阶段1: 解答
solve_response = deepseek_api.call(
    prompt=competition_solve_prompt + question,
    stream=True
)

# 阶段2: 验证
verify_response = deepseek_api.call(
    prompt=verification_prompt + question + solve_response.answer,
    stream=True
)
```

#### 3.2 图片问题（豆包）
```python
# 阶段1: 解答（带图片）
solve_response = doubao_api.stream_with_reasoning(
    text=question,
    image_path=image_path,
    subject=subject,
    mode='competition'
)

# 阶段2: 验证（纯文本，不需要再传图片）
verify_response = doubao_api.stream_with_reasoning(
    text=verification_prompt + solve_response.answer,
    subject=subject,
    mode='verify'
)
```

### 4. 新增提示词设计

#### 4.1 竞赛解答提示词 (Competition Solve Prompt)
```
你是一位国际奥赛金牌教练，擅长解决高难度竞赛问题。

解题要求：
1. 深入分析问题本质，寻找关键突破点
2. 考虑多种解法，选择最优雅的方案
3. 详细展示推导过程，每一步都要有理有据
4. 注意边界条件和特殊情况
5. 给出明确的最终答案

输出格式：
## 问题分析
[分析题目条件和要求]

## 解题思路
[说明采用的方法和原因]

## 详细解答
[完整的解题过程]

## 最终答案
[明确的答案，用 \\boxed{} 标注]
```

#### 4.2 答案验证提示词 (Verification Prompt)
```
你是一位严谨的数学/物理/化学审稿人，请验证以下解答的正确性。

原始问题：
{question}

待验证的解答：
{answer}

请从以下方面验证：
1. 计算过程是否正确（重新计算关键步骤）
2. 物理/化学原理是否正确应用
3. 单位和量纲是否一致
4. 是否考虑了所有边界条件
5. 最终答案是否合理

输出格式：
## 验证结果
[✓ 正确 / ⚠ 发现问题]

## 验证过程
[关键步骤的独立验算]

## 发现的问题（如有）
[具体指出错误并给出修正]

## 修正后的答案（如需要）
[正确的答案]
```

### 5. 后端实现步骤

#### Step 1: 修改 session 数据结构
```python
session_data = {
    'question': question,
    'subject': subject,
    'deep_think': True,  # 新增：深度思考标记
    'timestamp': str(datetime.now()),
    'type': 'text' | 'image_stream',
    # 深度思考模式下的额外字段
    'workflow_stage': 'solving' | 'verifying' | 'done',
    'solve_result': {...},
    'verify_result': {...}
}
```

#### Step 2: 新增深度思考流式端点
```python
@app.route('/api/stream/deep/<session_id>', methods=['GET'])
def stream_deep_response(session_id):
    """深度思考模式的流式响应"""
    # 阶段1: 解答
    # 阶段2: 验证
    # 阶段3: 整合
```

#### Step 3: 修改现有端点支持 deep_think 参数
```python
# /api/query/text
deep_think = data.get('deep_think', False)
session_data['deep_think'] = deep_think

# /api/query/image
deep_think = request.form.get('deep_think', 'false') == 'true'
session_data['deep_think'] = deep_think
```

### 6. 前端实现步骤

#### Step 1: 修改 result.html 支持多阶段显示
- 添加验证阶段的UI组件
- 支持阶段切换动画
- 显示当前工作流进度

#### Step 2: 修改 SSE 处理逻辑
```javascript
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);

    switch(data.type) {
        case 'stage':
            // 新增：处理阶段切换
            updateStageUI(data.stage);
            break;
        case 'thinking':
            appendToCurrentStage('thinking', data.content);
            break;
        case 'answer':
            appendToCurrentStage('answer', data.content);
            break;
        case 'verification':
            // 新增：验证结果
            showVerificationResult(data);
            break;
        case 'done':
            finalizeResults();
            break;
    }
};
```

### 7. SSE 事件设计

```javascript
// 阶段1开始
{ type: 'stage', stage: 'solving', message: '正在解答问题...' }

// 思考过程
{ type: 'thinking', content: '...' }

// 初步答案
{ type: 'answer', content: '...' }

// 阶段1完成，阶段2开始
{ type: 'stage', stage: 'verifying', message: '正在验证答案...' }

// 验证思考
{ type: 'verify_thinking', content: '...' }

// 验证结果
{ type: 'verification', passed: true/false, issues: [...], corrected_answer: '...' }

// 全部完成
{ type: 'done', final_answer: '...' }
```

### 8. 实现优先级

#### P0 - 核心功能（必须实现）
1. 后端：接收 deep_think 参数并存储到 session
2. 后端：实现两阶段调用逻辑（解答 → 验证）
3. 后端：实现深度思考 SSE 流式端点
4. 前端：result.html 支持多阶段显示

#### P1 - 增强功能（建议实现）
5. 竞赛级专业提示词
6. 验证提示词
7. 前端阶段切换动画
8. 验证结果可视化（通过/失败标记）

#### P2 - 优化功能（可选实现）
9. 验证失败时自动重新解答
10. 多种验证策略（数值验证、逻辑验证）
11. 解答质量评分
12. 历史记录和对比

## 文件修改清单

| 文件 | 修改内容 |
|------|----------|
| `src/app.py` | 添加 deep_think 参数处理，新增深度思考端点 |
| `src/doubao_api.py` | 添加竞赛模式和验证模式 |
| `src/prompts.py` | 添加竞赛解答和验证提示词 |
| `frontend/templates/result.html` | 多阶段UI显示 |
| `frontend/static/js/script.js` | SSE处理逻辑（已完成 deep_think 参数传递） |

## 预估工作量

- 后端核心逻辑：2-3小时
- 提示词设计调优：1-2小时
- 前端多阶段UI：2-3小时
- 测试和调试：1-2小时

**总计：6-10小时**
