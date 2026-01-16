#!/usr/bin/env python3
"""Simple question generator from a book text file."""

import argparse
import json
import re
from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Question:
    question: str
    answer: str
    source_sentence: str


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?。！？])\s+")


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def split_sentences(text: str) -> List[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    sentences = _SENTENCE_SPLIT_RE.split(cleaned)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def generate_questions(sentences: Iterable[str]) -> List[Question]:
    questions: List[Question] = []
    patterns = [
        (
            re.compile(r"^(?P<subject>.+?)\s+is\s+(?P<object>.+?)\.?$", re.IGNORECASE),
            "What is {subject}?",
        ),
        (
            re.compile(
                r"^(?P<subject>.+?)\s+was born in\s+(?P<object>.+?)\.?$",
                re.IGNORECASE,
            ),
            "Where was {subject} born?",
        ),
        (
            re.compile(
                r"^(?P<subject>.+?)\s+was born on\s+(?P<object>.+?)\.?$",
                re.IGNORECASE,
            ),
            "When was {subject} born?",
        ),
        (
            re.compile(
                r"^(?P<subject>.+?)\s+invented\s+(?P<object>.+?)\.?$",
                re.IGNORECASE,
            ),
            "What did {subject} invent?",
        ),
        (
            re.compile(
                r"^(?P<subject>.+?)\s+created\s+(?P<object>.+?)\.?$",
                re.IGNORECASE,
            ),
            "What did {subject} create?",
        ),
    ]

    for sentence in sentences:
        for pattern, template in patterns:
            match = pattern.match(sentence)
            if not match:
                continue
            subject = match.group("subject").strip()
            obj = match.group("object").strip()
            questions.append(
                Question(
                    question=template.format(subject=subject),
                    answer=obj,
                    source_sentence=sentence,
                )
            )
            break
    return questions


def format_output(questions: List[Question], output_format: str) -> str:
    if output_format == "json":
        payload = [question.__dict__ for question in questions]
        return json.dumps(payload, ensure_ascii=False, indent=2)
    lines = []
    for idx, question in enumerate(questions, start=1):
        lines.append(f"Q{idx}: {question.question}")
        lines.append(f"A{idx}: {question.answer}")
        lines.append(f"Source: {question.source_sentence}")
        lines.append("")
    return "\n".join(lines).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate questions from a book text file."
    )
    parser.add_argument("book", help="Path to the book text file")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = load_text(args.book)
    sentences = split_sentences(text)
    questions = generate_questions(sentences)
    output = format_output(questions, args.format)
    print(output)


if __name__ == "__main__":
    main()
