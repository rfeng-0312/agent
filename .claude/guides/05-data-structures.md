# 第5课：列表和字典

## 🎯 学习目标
- 理解列表（List）的使用
- 掌握字典（Dictionary）的操作
- 学会选择合适的数据结构
- 了解元组和集合

## 📦 列表（List）- 有序的数据集合

列表就像一个购物清单，可以按顺序存储多个数据：

### 创建列表

```python
# 创建空列表
empty_list = []

# 创建带数据的列表
fruits = ["苹果", "香蕉", "橙子"]
numbers = [1, 2, 3, 4, 5]
mixed = ["小明", 18, True, 175.5]  # 可以存不同类型的数据
```

### 访问列表元素

```python
fruits = ["苹果", "香蕉", "橙子"]

# 索引从0开始
print(fruits[0])  # 输出：苹果
print(fruits[1])  # 输出：香蕉
print(fruits[2])  # 输出：橙子

# 负数索引从后往前
print(fruits[-1])  # 输出：橙子（最后一个）
print(fruits[-2])  # 输出：香蕉（倒数第二个）
```

### 列表操作

```python
fruits = ["苹果", "香蕉"]

# 添加元素
fruits.append("橙子")  # 添加到末尾
fruits.insert(0, "葡萄")  # 插入到指定位置

# 删除元素
fruits.remove("香蕉")  # 删除指定值
removed = fruits.pop()  # 删除并返回最后一个

# 修改元素
fruits[0] = "草莓"  # 修改第一个元素

# 列表长度
print(len(fruits))  # 输出列表中元素的数量
```

### 列表切片

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 获取一部分
print(numbers[2:5])  # 输出：[2, 3, 4]（包含2，不包含5）
print(numbers[:3])   # 输出：[0, 1, 2]（前3个）
print(numbers[7:])   # 输出：[7, 8, 9]（从第7个开始）
print(numbers[::2])  # 输出：[0, 2, 4, 6, 8]（每隔一个取一个）
```

### 遍历列表

```python
fruits = ["苹果", "香蕉", "橙子"]

# 方法1：直接遍历
for fruit in fruits:
    print("我喜欢吃：" + fruit)

# 方法2：带索引遍历
for index, fruit in enumerate(fruits):
    print(f"第{index + 1}个水果是：{fruit}")
```

## 🗂️ 字典（Dictionary）- 键值对集合

字典就像一本真正的字典，通过"键"查找"值"：

### 创建字典

```python
# 创建空字典
empty_dict = {}

# 创建带数据的字典
student = {
    "name": "小明",
    "age": 18,
    "city": "北京",
    "grades": [85, 92, 78]
}
```

### 访问字典

```python
student = {
    "name": "小明",
    "age": 18,
    "city": "北京"
}

# 使用键访问值
print(student["name"])  # 输出：小明
print(student["age"])   # 输出：18

# 使用get方法（更安全）
print(student.get("name"))      # 输出：小明
print(student.get("country"))   # 输出：None（不存在时不报错）
print(student.get("country", "中国"))  # 输出：中国（默认值）
```

### 字典操作

```python
student = {"name": "小明", "age": 18}

# 添加或修改
student["city"] = "北京"  # 添加新键值对
student["age"] = 19       # 修改已有键的值

# 删除
del student["city"]       # 删除指定键
value = student.pop("age")  # 删除并返回值

# 检查键是否存在
if "name" in student:
    print("有name这个键")

# 获取所有键、值、键值对
print(student.keys())    # 输出所有键
print(student.values())  # 输出所有值
print(student.items())   # 输出所有键值对
```

### 遍历字典

```python
student = {
    "name": "小明",
    "age": 18,
    "city": "北京"
}

# 遍历键
for key in student:
    print(f"键：{key}")

# 遍历值
for value in student.values():
    print(f"值：{value}")

# 遍历键值对
for key, value in student.items():
    print(f"{key}: {value}")
```

## 🎮 综合示例

```python
# 学生成绩管理系统
students = []

# 添加学生
def add_student(name, chinese, math, english):
    student = {
        "name": name,
        "scores": {
            "语文": chinese,
            "数学": math,
            "英语": english
        }
    }
    students.append(student)

# 计算平均分
def calculate_average(student):
    scores = student["scores"].values()
    return sum(scores) / len(scores)

# 添加学生数据
add_student("小明", 85, 92, 78)
add_student("小红", 90, 88, 95)
add_student("小刚", 78, 85, 82)

# 打印成绩单
print("成绩单")
print("=" * 40)
for student in students:
    avg = calculate_average(student)
    print(f"姓名：{student['name']}")
    print(f"语文：{student['scores']['语文']}")
    print(f"数学：{student['scores']['数学']}")
    print(f"英语：{student['scores']['英语']}")
    print(f"平均分：{avg:.1f}")
    print("-" * 40)
```

## 🏗️ 项目中的实际应用

在我们的项目中：

```python
# 1. 存储允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 2. 存储用户上传的文件信息
uploaded_files = [
    {
        "filename": "photo1.jpg",
        "size": 1024000,
        "user": "小明",
        "upload_time": "2025-12-06 10:30:00"
    },
    {
        "filename": "doc.pdf",
        "size": 2048000,
        "user": "小红",
        "upload_time": "2025-12-06 11:15:00"
    }
]

# 3. 存储API响应数据
response_data = {
    "status": "success",
    "data": {
        "answer": "根据牛顿第二定律...",
        "confidence": 0.95,
        "sources": ["教材第3章", "练习册第5题"]
    },
    "timestamp": "2025-12-06T12:00:00Z"
}

# 4. 存储会话信息
user_session = {
    "user_id": "user123",
    "login_time": "2025-12-06 09:00:00",
    "questions_asked": [],
    "is_active": True
}
```

## 📊 其他数据结构

### 元组（Tuple）- 不可变的列表

```python
# 创建元组
coordinates = (10, 20)
colors = ("红", "绿", "蓝")

# 访问（和列表一样）
print(coordinates[0])  # 输出：10

# 特点：不能修改
# coordinates[0] = 15  # 这行会报错！

# 使用场景：存储不变的数据
point = (3, 4)  # 二维坐标
rgb = (255, 0, 0)  # 红色
```

### 集合（Set）- 不重复的元素

```python
# 创建集合
unique_numbers = {1, 2, 3, 3, 4, 4, 5}
print(unique_numbers)  # 输出：{1, 2, 3, 4, 5}（自动去重）

# 集合运算
a = {1, 2, 3}
b = {3, 4, 5}

print(a | b)  # 并集：{1, 2, 3, 4, 5}
print(a & b)  # 交集：{3}
print(a - b)  # 差集：{1, 2}
```

## ✏️ 小练习

1. 创建一个购物车列表，添加5个商品，计算总价
2. 创建一个通讯录字典，存储3个朋友的姓名和电话
3. 使用列表和字典结合，存储一个班级的学生信息

```python
# 练习1答案
shopping_cart = [
    {"name": "苹果", "price": 5.5, "quantity": 2},
    {"name": "牛奶", "price": 8.0, "quantity": 1},
    {"name": "面包", "price": 12.0, "quantity": 1},
    {"name": "鸡蛋", "price": 1.0, "quantity": 10},
    {"name": "巧克力", "price": 15.0, "quantity": 1}
]

total = 0
for item in shopping_cart:
    subtotal = item["price"] * item["quantity"]
    total += subtotal
    print(f"{item['name']}: {subtotal}元")

print(f"总价：{total}元")
```

## 💡 选择合适的数据结构

| 场景 | 推荐的数据结构 |
|------|---------------|
| 有顺序的数据，需要增删 | 列表（List） |
| 键值对数据，需要快速查找 | 字典（Dictionary） |
| 数据不会改变 | 元组（Tuple） |
| 需要去重 | 集合（Set） |

## 🤔 思考题

```python
data = [
    {"name": "小明", "score": 85},
    {"name": "小红", "score": 92},
    {"name": "小刚", "score": 78}
]

# 如何找出分数最高的学生？
```

**答案：**
```python
max_student = data[0]
for student in data:
    if student["score"] > max_student["score"]:
        max_student = student
print(f"最高分学生：{max_student['name']}")
```

## 🎉 下节课预告

下节课我们将学习：
- 文件的读取和写入
- 如何保存数据到文件
- 处理CSV和JSON文件

---

**记住：选择合适的数据结构，能让程序更简单高效！** 🏗️

[下一课：文件操作 →](06-file-operations.md)