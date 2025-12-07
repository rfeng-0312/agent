# 性能优化建议

## 🎯 当前问题

豆包API响应速度慢，可能的原因：
1. 图片处理时间长
2. 高精度模式（detail: "high"）增加处理时间
3. Token生成数量过多（max_tokens: 4096）
4. 不支持的API参数导致额外处理

## ✅ 已实施的优化

### 1. 图片压缩优化
- 使用PIL库自动压缩图片到1024x1024以下
- JPEG质量设置为85%
- 转换为RGB模式减少兼容性问题

### 2. 精度模式优化
- 默认使用低精度模式（detail: "low"）
- 移除了可能不支持的API参数

### 3. Token数量优化
- 减少max_tokens到2048（首次尝试）
- 失败时进一步减少到1024

### 4. 错误处理优化
- 添加了重试机制
- 降低了图片精度作为备选方案

## 🔧 额外优化建议

### 1. 安装必要的依赖
```bash
pip install Pillow volcengine-python-sdk[ark]
```

### 2. 前端优化
- 添加加载指示器显示处理进度
- 实现图片压缩在前端
- 限制上传文件大小（如2MB）

### 3. 缓存机制
```python
# 可以考虑添加缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(image_hash, question):
    # 缓存相同图片和问题的答案
    pass
```

### 4. 异步处理
考虑使用异步处理大图片：
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

def process_image_async(image_path, question):
    future = executor.submit(process_image, image_path, question)
    return future
```

### 5. 流式响应
实现流式响应让用户看到实时生成的内容：
```javascript
// 前端示例
fetch('/api/query/stream', {
    method: 'POST',
    body: formData
})
.then(response => {
    const reader = response.body.getReader();
    // 处理流式数据
});
```

### 6. 图片预处理建议
在上传前进行以下处理：
- 限制图片宽高在1024px以内
- 使用WebP格式（更小）
- 调整JPEG质量到80-90
- 裁剪无关区域

## 📊 性能监控

### 添加性能日志
```python
import time

start_time = time.time()
# API调用
end_time = time.time()
logger.info(f"API响应时间: {end_time - start_time:.2f}秒")
```

### 监控指标
- API响应时间
- 图片大小和处理时间
- Token使用量
- 成功率

## ⚠️ 注意事项

1. **PIL安装**
   - Windows: 可能需要安装Visual C++构建工具
   - Linux: `sudo apt-get install python3-pil libjpeg-dev`
   - Mac: `brew install pillow`

2. **API限制**
   - 注意豆包API的调用频率限制
   - 监控每日token使用量

3. **用户体验**
   - 添加进度条
   - 提供取消功能
   - 超时处理（如30秒超时）

## 🎯 推荐配置

### 快速响应配置（适合简单问题）
- 图片精度：low
- max_tokens：1024
- 图片尺寸：800x800

### 高质量配置（适合复杂问题）
- 图片精度：high（仅在需要时）
- max_tokens：2048
- 图片尺寸：1024x1024

---

**更新时间**: 2025-12-06
**版本**: 1.0.0