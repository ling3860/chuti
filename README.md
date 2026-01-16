# 出题软件（原型）

这个原型脚本用于从一本书的纯文本内容中提取可生成题目的句子，并输出问答对。

## 功能

- 读取文本文件。
- 基于简单句型（如 "X is Y"、"X was born in Y"）生成问题。
- 支持输出为纯文本或 JSON。

## 使用方式

```bash
python3 main.py /path/to/book.txt --format json
```

示例输出（文本）：

```
Q1: What is Isaac Newton?
A1: an English physicist
Source: Isaac Newton is an English physicist.
```

> 说明：目前仅支持有限的英文句型模板，可根据需要扩展规则或改为更强的 NLP 模型。
