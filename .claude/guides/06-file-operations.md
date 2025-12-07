# 第6课：文件操作

## 🎯 学习目标
- 学会读取文件内容
- 掌握写入文件的方法
- 理解文件路径的概念
- 学会处理JSON和CSV文件

## 💾 为什么需要文件操作？

程序运行结束后，变量都会消失。想要保存数据，就需要文件：

- 保存用户设置
- 存储数据记录
- 读取配置信息
- 保存程序日志

## 📂 文件路径

### 绝对路径 vs 相对路径

```python
# 绝对路径：从根目录开始的完整路径
# Windows: "C:\\Users\\小明\\Desktop\\文件.txt"
# Mac/Linux: "/home/小明/文件.txt"

# 相对路径：从当前文件位置开始的路径
"config.txt"          # 当前目录下的config.txt
"data/info.txt"       # 当前目录下data文件夹里的info.txt
"../settings.txt"     # 上一级目录的settings.txt
```

## 📖 读取文件

### 基本读取

```python
# 方法1：完整方式（推荐）
file = open("test.txt", "r", encoding="utf-8")  # r = read
content = file.read()
print(content)
file.close()  # 必须关闭文件！

# 方法2：使用with语句（自动关闭）
with open("test.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)
    # 文件会自动关闭
```

### 逐行读取

```python
with open("lines.txt", "r", encoding="utf-8") as file:
    for line in file:
        # line包含换行符\n，用strip()去除
        print(line.strip())
```

### 读取到列表

```python
with open("lines.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()  # 读取所有行到列表
    for line in lines:
        print(line.strip())
```

## ✏️ 写入文件

### 覆盖写入

```python
# w = write（覆盖原有内容）
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("第一行\n")
    file.write("第二行\n")
    file.write("第三行\n")
```

### 追加写入

```python
# a = append（在文件末尾添加）
with open("output.txt", "a", encoding="utf-8") as file:
    file.write("这是追加的内容\n")
```

### 写入列表

```python
lines = ["第一行", "第二行", "第三行"]
with open("output.txt", "w", encoding="utf-8") as file:
    for line in lines:
        file.write(line + "\n")  # 手动添加换行符
```

## 🗂️ 处理JSON文件

JSON是常用的数据交换格式：

### 读取JSON

```python
import json

# 读取JSON文件
with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)  # 转换为Python对象

# 使用数据
print(data["name"])
print(data["age"])
for hobby in data["hobbies"]:
    print(hobby)
```

### 写入JSON

```python
import json

# Python数据
data = {
    "name": "小明",
    "age": 18,
    "city": "北京",
    "hobbies": ["编程", "阅读", "运动"]
}

# 写入JSON文件
with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)
    # ensure_ascii=False 支持中文
    # indent=2 格式化缩进
```

## 📊 处理CSV文件

CSV是表格数据存储格式：

```python
import csv

# 读取CSV
with open("students.csv", "r", encoding="utf-8", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        print(f"姓名：{row[0]}, 年龄：{row[1]}, 成绩：{row[2]}")

# 写入CSV
students = [
    ["小明", "18", "85"],
    ["小红", "19", "92"],
    ["小刚", "18", "78"]
]

with open("students.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["姓名", "年龄", "成绩"])  # 写入表头
    writer.writerows(students)  # 写入所有数据
```

## 🎮 实际示例：记事本程序

```python
def add_note():
    """添加新笔记"""
    note = input("请输入笔记内容：")
    timestamp = input("请输入日期时间（回车使用当前时间）：")

    if not timestamp:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("notes.txt", "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {note}\n")

    print("笔记已保存！")

def view_notes():
    """查看所有笔记"""
    try:
        with open("notes.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            if not lines:
                print("还没有任何笔记")
            else:
                print("\n=== 所有笔记 ===")
                for i, line in enumerate(lines, 1):
                    print(f"{i}. {line.strip()}")
    except FileNotFoundError:
        print("还没有任何笔记")

def search_notes():
    """搜索笔记"""
    keyword = input("请输入搜索关键词：")

    with open("notes.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
        found = False

        for line in lines:
            if keyword in line:
                print(line.strip())
                found = True

        if not found:
            print(f"没有找到包含'{keyword}'的笔记")

# 主程序
while True:
    print("\n=== 我的记事本 ===")
    print("1. 添加笔记")
    print("2. 查看所有笔记")
    print("3. 搜索笔记")
    print("4. 退出")

    choice = input("请选择操作（1-4）：")

    if choice == "1":
        add_note()
    elif choice == "2":
        view_notes()
    elif choice == "3":
        search_notes()
    elif choice == "4":
        print("再见！")
        break
    else:
        print("无效的选择，请重试")
```

## 🏗️ 项目中的实际应用

在我们的项目中：

```python
# 1. 读取环境变量配置
def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)

config = load_config()
api_key = config["deepseek_api_key"]

# 2. 保存用户上传记录
def save_upload_info(filename, user_id):
    record = {
        "filename": filename,
        "user_id": user_id,
        "upload_time": datetime.now().isoformat()
    }

    with open("uploads.json", "a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

# 3. 读取提示词模板
def load_prompt_template():
    with open("prompts.txt", "r", encoding="utf-8") as file:
        return file.read()

# 4. 保存API调用日志
def log_api_call(endpoint, params, response):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "params": params,
        "response": response[:100]  # 只保存前100个字符
    }

    with open("api_logs.jsonl", "a", encoding="utf-8") as file:
        file.write(json.dumps(log_entry) + "\n")
```

## ✏️ 小练习

1. 创建一个程序，让用户输入信息并保存到文件
2. 读取文件并统计行数和单词数
3. 创建一个简单的通讯录，可以添加、查看和搜索联系人

```python
# 练习3答案 - 简单通讯录
import json

def add_contact():
    name = input("姓名：")
    phone = input("电话：")
    email = input("邮箱：")

    contact = {"name": name, "phone": phone, "email": email}

    # 读取现有联系人
    try:
        with open("contacts.json", "r", encoding="utf-8") as file:
            contacts = json.load(file)
    except:
        contacts = []

    contacts.append(contact)

    # 保存更新后的联系人
    with open("contacts.json", "w", encoding="utf-8") as file:
        json.dump(contacts, file, ensure_ascii=False, indent=2)

    print(f"已添加联系人：{name}")
```

## 💡 文件操作注意事项

1. **总是使用with语句**
   - 自动关闭文件
   - 处理异常情况

2. **指定正确的编码**
   - `encoding="utf-8"` 支持中文
   - Windows可能需要 `encoding="gbk"`

3. **处理文件不存在的情况**
```python
try:
    with open("data.txt", "r") as file:
        content = file.read()
except FileNotFoundError:
    print("文件不存在")
```

4. **处理大文件**
```python
# 不要一次性读取大文件
# 使用逐行读取
with open("big_file.txt", "r") as file:
    for line in file:
        process_line(line)
```

## 🤔 思考题

```python
# 如何计算一个文件中有多少个不重复的单词？
```

**答案：**
```python
def count_unique_words(filename):
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read().lower()  # 转为小写

    # 分割单词（简单方式）
    words = content.split()

    # 使用集合去重
    unique_words = set(words)

    return len(unique_words)
```

## 🎉 下节课预告

下节课我们将学习：
- 什么是Web应用
- HTTP协议基础
- 前端和后端的关系

---

**记住：文件操作让数据可以永久保存，是程序的重要组成部分！** 💾

[下一课：了解什么是Web →](07-web-basics.md)