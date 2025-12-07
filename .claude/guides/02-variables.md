# 第2课：变量和数据类型

## 🎯 学习目标
- 理解什么是变量
- 学会创建和使用变量
- 了解不同的数据类型

## 💭 什么是变量？

想象变量是一个带标签的盒子：
- 盒子可以装东西
- 标签告诉你盒子里装的是什么
- 你可以随时更换盒子里的东西

**在编程中，变量就是存储数据的容器**

## 📦 创建变量

```python
name = "小明"
age = 18
height = 175.5
is_student = True
```

**解释：**
- `name` 是一个变量，存储了文字"小明"
- `age` 存储了数字18
- `height` 存储了小数175.5
- `is_student` 存储了是或否（True/False）

## 🔤 变量的命名规则

1. 只能使用字母、数字和下划线
2. 不能以数字开头
3. 区分大小写（name和Name是不同的）
4. 要用有意义的名字

**好的例子：**
```python
user_name = "张三"
student_age = 20
total_score = 95.5
```

**不好的例子：**
```python
n = "张三"  # 太短，不清楚
123abc = 20  # 不能数字开头
user-name = "李四"  # 不能用减号
```

## 📊 数据类型

### 1. 字符串（str）- 文字
```python
name = "小明"  # 双引号
message = '你好'  # 单引号也行
story = "他说：'今天天气真好！'"  # 嵌套使用
```

### 2. 数字（int 和 float）
```python
# 整数（没有小数点）
count = 10
year = 2025

# 小数（有小数点）
price = 19.99
temperature = 36.5
```

### 3. 布尔值（bool）- 真或假
```python
is_raining = True
is_sunny = False
has_finished = True
```

## 🎮 使用变量

```python
# 创建变量
name = "小红"
age = 17
city = "北京"

# 使用变量
print("姓名：" + name)
print("年龄：" + str(age))  # str() 把数字变成文字
print("城市：" + city)

# 变量可以改变
age = 18  # 过生日了！
print("现在的年龄：" + str(age))
```

## 🏗️ 项目中的实际应用

在我们的项目中有这样的变量：

```python
# 存储配置信息
UPLOAD_FOLDER = '../data/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 存储API密钥（需要保密）
API_KEY = "sk-123456789"

# 存储文件名
filename = "styles.css"
```

## ✏️ 小练习

1. 创建一个变量存储你的名字，然后打印出来
2. 创建一个变量存储你的年龄，明年几岁？
3. 创建一个变量存储你喜欢的水果

```python
# 练习答案
my_name = "你的名字"
my_age = 你的年龄
next_year_age = my_age + 1  # 明年的年龄
favorite_fruit = "苹果"

print("我的名字是：" + my_name)
print("明年我" + str(next_year_age) + "岁")
print("我喜欢吃：" + favorite_fruit)
```

## 💡 小技巧

```python
# f-string - 更方便的输出方式
name = "小华"
age = 20
print(f"我叫{name}，今年{age}岁")
# 输出：我叫小华，今年20岁
```

## 🤔 思考题

```python
x = 10
y = x
x = 20
print(y)  # 会输出什么？
```

**答案：10**
因为y存储的是x最初的值（10），后来x改变不影响y

## 🎉 下节课预告

下节课我们将学习：
- 什么是函数（def）
- 如何创建自己的命令
- 如何让代码重复使用

---

**记住：变量就像是程序的记事本，帮助记住重要的信息！** 📝

[下一课：函数 - def的魔法 →](03-functions.md)