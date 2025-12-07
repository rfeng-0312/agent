# 答案展示页面修复计划

## 问题分析

根据用户反馈的示例：
```
计算过程

步骤1：计算n(S₂O₃²⁻)
[
n(S_2O_3^{2-}) = c \times V = 0.1020\ $\text{mol/L} \times 26.43\ $\text{mL} \times 10^{-3}\ $\text{L/mL} = 0.00269586\ $\text{mol}
]

最终答案
(\boxed{0.1078\ \text{mol/L}})
```

### 问题1: 每行之间有多余的换行
**原因**: `whitespace-pre-wrap` CSS属性 + `marked.js` 的 `breaks: true` 导致双重换行处理

### 问题2: 公式显示为乱码
**原因**:
- 豆包返回的是LaTeX格式，使用 `[...]` 和 `(...)` 作为公式定界符（而非 `$$...$$` 和 `$...$`）
- 正则表达式没有匹配这些格式
- `\boxed{}` 等命令没有被正确转为KaTeX可渲染的格式

### 问题3: 方括号 `[...]` 包裹步骤
**原因**: 豆包返回的块级公式使用 `[...]` 定界符，没有被识别和渲染

## 修复方案

### 步骤1: 修改CSS样式
1. 移除 `whitespace-pre-wrap`，改用正常的段落处理
2. 添加更好的段落和列表样式
3. 优化公式显示区域的样式

### 步骤2: 改进LaTeX公式识别
1. 添加对 `\[...\]` 块级公式的支持
2. 添加对 `\(...\)` 行内公式的支持
3. 添加对 `[...]` 和 `(...)` 定界符的支持（豆包格式）
4. 改进 `\boxed{}` 等命令的处理

### 步骤3: 优化Markdown渲染
1. 关闭 `breaks: true`，让段落更自然
2. 添加后处理步骤清理多余空行
3. 确保标题、列表、代码块正确渲染

### 步骤4: 添加化学式支持
1. 使用 mhchem 扩展来渲染化学式（如 H₂O, KMnO₄）
2. 或者用正则预处理将 Unicode 下标转为 LaTeX 格式

## 具体实现

### CSS修改
```css
#answerText {
    line-height: 1.8;
    /* 移除 whitespace-pre-wrap */
}

#answerText p {
    margin: 0.8em 0;
}

/* 块级公式居中显示 */
.katex-display {
    text-align: center;
    margin: 1.5em 0;
    padding: 1em;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 8px;
}
```

### JavaScript修改
```javascript
function renderMarkdown(elementId, markdownText) {
    let text = markdownText;

    // 1. 标准化换行符
    text = text.replace(/\r\n/g, '\n');

    // 2. 处理豆包格式的块级公式 [...] -> $$...$$
    text = text.replace(/\[\s*\n?([\s\S]+?)\n?\s*\]/g, (match, formula) => {
        // 确保不是Markdown链接 [text](url)
        if (formula.includes('](')) return match;
        return '\n$$' + formula.trim() + '$$\n';
    });

    // 3. 处理豆包格式的行内公式 (...) -> $...$
    text = text.replace(/\(\\[a-zA-Z]+[\s\S]*?\)/g, (match) => {
        return '$' + match.slice(1, -1) + '$';
    });

    // 4. 处理标准LaTeX定界符 \[...\] 和 \(...\)
    text = text.replace(/\\\[([\s\S]+?)\\\]/g, '$$$$1$$');
    text = text.replace(/\\\(([\s\S]+?)\\\)/g, '$$$1$');

    // ... 后续处理
}
```

## 测试用例

1. 块级公式测试：
   - `[n = c \times V]` 应渲染为居中的数学公式

2. 行内公式测试：
   - `(\boxed{0.1078})` 应渲染为带框的数字

3. 化学式测试：
   - `KMnO₄` 应正确显示下标
   - `S₂O₃²⁻` 应正确显示上下标

4. Markdown测试：
   - `**加粗**` 应显示为粗体
   - `步骤1：` 应正常显示，无多余换行
