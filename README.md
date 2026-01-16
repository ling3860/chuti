# 出题软件（原型）

这个原型脚本用于从一本书的纯文本内容中提取可生成题目的句子，并输出问答对。

## 功能

- 读取文本文件。
- 基于简单句型（如 "X is Y"、"X was born in Y"、"X是Y"、"X出生于Y"）生成问题。
- 支持问答题、选择题、判断题。
- 支持输出为纯文本或 JSON。

## 使用方式

使用根目录下的可执行脚本运行：

```bash
# 输出 JSON（全部题型）
./run_questions.sh /path/to/book.txt --question-type all --format json

# 仅生成中文选择题
./run_questions.sh /path/to/book.txt --question-type mcq --choices 4
```

示例输出（文本）：

```
Q1: 以下哪项描述了爱因斯坦？
  A. 德国物理学家
  B. 英国文学家
  C. 法国画家
  D. 意大利工程师
A1: 德国物理学家
Source: 爱因斯坦是德国物理学家。
```

> 说明：目前仅支持有限的中英文句型模板，可根据需要扩展规则或改为更强的 NLP 模型。
