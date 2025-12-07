# 豆包API集成文档

## 📋 概述

本文档描述了如何在名侦探作业帮项目中集成和使用豆包API来处理带图片的物理和化学问题。

## 🔧 技术细节

### API信息
- **API提供商**: 字节跳动豆包
- **模型**: doubao-seed-1-6-251015
- **API Key**: a7ce8af1-5b59-467b-984e-4d0934976e80
- **Base URL**: https://ark.cn-beijing.volces.com/api/v3

### 功能特性
1. **图片理解**: 支持多种图片格式（PNG、JPEG、GIF、WEBP等）
2. **高精度模式**: 使用"detail": "high"进行精细图片分析
3. **深度思考**: 启用高级推理模式
4. **联网搜索**: 支持实时信息查询
5. **专业提示词**: 针对物理和化学优化的专业提示

## 📁 文件结构

```
src/
├── doubao_api.py          # 豆包API客户端
├── app.py                 # Flask应用（已集成）
└── .env                   # 环境变量配置
```

## 🚀 使用方法

### 1. 环境配置

在 `src/.env` 文件中添加：
```env
DOUBAO_API_KEY=a7ce8af1-5b59-467b-984e-4d0934976e80
```

### 2. 基本使用

```python
from doubao_api import DoubaoClient

# 创建客户端
client = DoubaoClient()

# 处理带图片的问题
response = client.solve_with_image(
    text="请解释这个物理现象",
    image_path="path/to/image.jpg",
    subject="physics",
    stream=False,
    enable_search=True
)

# 获取答案
answer = response['content']
```

### 3. API端点

#### 上传图片文件
- **端点**: `/api/query/image`
- **方法**: POST
- **参数**:
  - `image`: 图片文件
  - `question`: 问题文本
  - `subject`: 学科（physics/chemistry）

#### Base64图片
- **端点**: `/api/query/base64`
- **方法**: POST
- **参数**:
  - `image`: Base64编码的图片
  - `question`: 问题文本
  - `subject`: 学科（physics/chemistry）

## 🎯 专业提示词

### 物理提示词特点
- 涵盖力学、电磁学、热学、光学、近代物理
- 强调物理图像和直观理解
- 培养物理思维和创新能力
- 联系实际应用

### 化学提示词特点
- 涵盖无机、有机、分析、物理化学
- 强调反应机理和实验设计
- 注重绿色化学理念
- 介绍最新化学进展

## ⚙️ 配置参数

### 模型参数
```python
{
    "model": "doubao-seed-1-6-251015",
    "max_tokens": 4096,
    "temperature": 0.3,
    "extra_body": {
        "search_enabled": True,     # 启用联网搜索
        "thinking_depth": "deep",  # 深度思考
        "reasoning_mode": "advanced"  # 高级推理
    }
}
```

### 图片参数
```python
{
    "type": "image_url",
    "image_url": {
        "url": "data:image/jpeg;base64,...",
        "detail": "high"  # 高精度模式
    }
}
```

## 🔍 测试

运行测试脚本验证功能：
```bash
python .claude/tests/temporary/test_doubao_api_20251206.py
```

## 📝 使用示例

### JavaScript前端调用

```javascript
// 上传图片文件
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('question', '请解释这个电路图');
formData.append('subject', 'physics');

fetch('/api/query/image', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.status === 'success') {
        window.location.href = data.redirect_url;
    }
});
```

### Base64方式

```javascript
const data = {
    image: base64String,
    question: '这个化学反应的机理是什么？',
    subject: 'chemistry'
};

fetch('/api/query/base64', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => {
    console.log(data);
});
```

## ⚠️ 注意事项

1. **图片大小限制**
   - 单张图片最大 10MB
   - 建议分辨率在 104万像素（low模式）或 401万像素（high模式）内

2. **支持格式**
   - JPEG、PNG、GIF、WEBP、BMP等
   - 文件扩展名必须与实际格式匹配

3. **API限制**
   - 注意API调用频率限制
   - 监控token使用量

4. **错误处理**
   - 所有错误都有详细日志
   - 前端需要处理API错误响应

## 🚨 故障排除

### 常见错误

1. **"No image provided"**
   - 确保正确上传图片或提供Base64数据

2. **"File type not allowed"**
   - 检查图片文件扩展名

3. **API调用失败**
   - 验证API密钥是否正确
   - 检查网络连接

### 调试方法

1. 查看Flask日志
2. 检查浏览器开发者工具
3. 运行测试脚本验证功能

## 📊 性能优化

1. **图片压缩**
   - 上传前压缩图片减少传输时间
   - 使用适当的图片格式

2. **缓存机制**
   - 考虑缓存常见问题的答案
   - 使用CDN加速静态资源

3. **异步处理**
   - 大图片或复杂问题使用流式响应
   - 避免阻塞主线程

---

**最后更新**: 2025-12-06
**版本**: 1.0.0