#!/usr/bin/env python3
"""Simple question generator from a book text file."""

import argparse
import json
import re
from dataclasses import dataclass
from random import Random
from typing import Iterable, List


@dataclass
class Fact:
    subject: str
    relation: str
    obj: str
    source_sentence: str
    language: str


@dataclass
class Question:
    question: str
    answer: str
    source_sentence: str


@dataclass
class MultipleChoiceQuestion:
    question: str
    answer: str
    options: List[str]
    source_sentence: str


@dataclass
class TrueFalseQuestion:
    statement: str
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


QA_TEMPLATES = {
    "is": {"en": "What is {subject}?", "zh": "{subject}是什么？"},
    "born_in": {"en": "Where was {subject} born?", "zh": "{subject}出生于哪里？"},
    "born_on": {"en": "When was {subject} born?", "zh": "{subject}出生于什么时候？"},
    "invented": {"en": "What did {subject} invent?", "zh": "{subject}发明了什么？"},
    "created": {"en": "What did {subject} create?", "zh": "{subject}创建了什么？"},
}

MCQ_TEMPLATES = {
    "is": {"en": "Which option describes {subject}?", "zh": "以下哪项描述了{subject}？"},
    "born_in": {"en": "Where was {subject} born?", "zh": "{subject}出生于哪里？"},
    "born_on": {"en": "When was {subject} born?", "zh": "{subject}出生于什么时候？"},
    "invented": {"en": "What did {subject} invent?", "zh": "{subject}发明了什么？"},
    "created": {"en": "What did {subject} create?", "zh": "{subject}创建了什么？"},
}

STATEMENT_TEMPLATES = {
    "is": {"en": "{subject} is {obj}.", "zh": "{subject}是{obj}。"},
    "born_in": {"en": "{subject} was born in {obj}.", "zh": "{subject}出生于{obj}。"},
    "born_on": {"en": "{subject} was born on {obj}.", "zh": "{subject}出生于{obj}。"},
    "invented": {"en": "{subject} invented {obj}.", "zh": "{subject}发明了{obj}。"},
    "created": {"en": "{subject} created {obj}.", "zh": "{subject}创建了{obj}。"},
}


def extract_facts(sentences: Iterable[str]) -> List[Fact]:
    facts: List[Fact] = []
    patterns = [
        (
            re.compile(r"^(?P<subject>.+?)\s+is\s+(?P<object>.+?)\.?$", re.IGNORECASE),
            "is",
            "en",
        ),
        (
            re.compile(
                r"^(?P<subject>.+?)\s+was born in\s+(?P<object>.+?)\.?$",
                re.IGNORECASE,
            ),
            "born_in",
            "en",
        ),
        (
            re.compile(
                r"^(?P<subject>.+?)\s+was born on\s+(?P<object>.+?)\.?$",
                re.IGNORECASE,
            ),
            "born_on",
            "en",
        ),
        (
            re.compile(
                r"^(?P<subject>.+?)\s+invented\s+(?P<object>.+?)\.?$",
                re.IGNORECASE,
            ),
            "invented",
            "en",
        ),
        (
            re.compile(
                r"^(?P<subject>.+?)\s+created\s+(?P<object>.+?)\.?$",
                re.IGNORECASE,
            ),
            "created",
            "en",
        ),
        (
            re.compile(r"^(?P<subject>.+?)是(?P<object>.+?)。?$"),
            "is",
            "zh",
        ),
        (
            re.compile(r"^(?P<subject>.+?)出生(?:于|在)(?P<object>.+?)。?$"),
            "born_in",
            "zh",
        ),
        (
            re.compile(
                r"^(?P<subject>.+?)出生于(?P<object>.+?(?:年|月|日).+?)。?$"
            ),
            "born_on",
            "zh",
        ),
        (
            re.compile(r"^(?P<subject>.+?)发明了?(?P<object>.+?)。?$"),
            "invented",
            "zh",
        ),
        (
            re.compile(r"^(?P<subject>.+?)创建了?(?P<object>.+?)。?$"),
            "created",
            "zh",
        ),
    ]

    for sentence in sentences:
        for pattern, relation, language in patterns:
            match = pattern.match(sentence)
            if not match:
                continue
            facts.append(
                Fact(
                    subject=match.group("subject").strip(),
                    relation=relation,
                    obj=match.group("object").strip(),
                    source_sentence=sentence,
                    language=language,
                )
            )
            break
    return facts


def generate_qa(facts: Iterable[Fact]) -> List[Question]:
    questions: List[Question] = []
    for fact in facts:
        template = QA_TEMPLATES.get(fact.relation, {}).get(fact.language)
        if not template:
            continue
        questions.append(
            Question(
                question=template.format(subject=fact.subject),
                answer=fact.obj,
                source_sentence=fact.source_sentence,
            )
        )
    return questions


def generate_mcq(
    facts: Iterable[Fact], choices_count: int, rng: Random
) -> List[MultipleChoiceQuestion]:
    questions: List[MultipleChoiceQuestion] = []
    fact_list = list(facts)
    distractor_pool = [fact.obj for fact in fact_list]
    for fact in fact_list:
        template = MCQ_TEMPLATES.get(fact.relation, {}).get(fact.language)
        if not template:
            continue
        candidates = [obj for obj in distractor_pool if obj != fact.obj]
        if not candidates:
            continue
        rng.shuffle(candidates)
        choices = [fact.obj] + candidates[: max(1, choices_count - 1)]
        rng.shuffle(choices)
        questions.append(
            MultipleChoiceQuestion(
                question=template.format(subject=fact.subject),
                answer=fact.obj,
                options=choices,
                source_sentence=fact.source_sentence,
            )
        )
    return questions


def generate_true_false(facts: Iterable[Fact], rng: Random) -> List[TrueFalseQuestion]:
    questions: List[TrueFalseQuestion] = []
    fact_list = list(facts)
    distractor_pool = [fact.obj for fact in fact_list]
    for fact in fact_list:
        template = STATEMENT_TEMPLATES.get(fact.relation, {}).get(fact.language)
        if not template:
            continue
        true_statement = template.format(subject=fact.subject, obj=fact.obj)
        questions.append(
            TrueFalseQuestion(
                statement=true_statement,
                answer="True" if fact.language == "en" else "正确",
                source_sentence=fact.source_sentence,
            )
        )
        candidates = [obj for obj in distractor_pool if obj != fact.obj]
        if candidates:
            false_obj = rng.choice(candidates)
            false_statement = template.format(subject=fact.subject, obj=false_obj)
            questions.append(
                TrueFalseQuestion(
                    statement=false_statement,
                    answer="False" if fact.language == "en" else "错误",
                    source_sentence=fact.source_sentence,
                )
            )
    return questions


def format_output(
    qa_questions: List[Question],
    mcq_questions: List[MultipleChoiceQuestion],
    tf_questions: List[TrueFalseQuestion],
    output_format: str,
) -> str:
    if output_format == "json":
        payload = []
        for item in qa_questions:
            payload.append(
                {
                    "type": "qa",
                    **item.__dict__,
                }
            )
        for item in mcq_questions:
            payload.append(
                {
                    "type": "mcq",
                    **item.__dict__,
                }
            )
        for item in tf_questions:
            payload.append(
                {
                    "type": "truefalse",
                    **item.__dict__,
                }
            )
        return json.dumps(payload, ensure_ascii=False, indent=2)
    lines = []
    index = 1
    for item in qa_questions:
        lines.append(f"Q{index}: {item.question}")
        lines.append(f"A{index}: {item.answer}")
        lines.append(f"Source: {item.source_sentence}")
        lines.append("")
        index += 1
    for item in mcq_questions:
        lines.append(f"Q{index}: {item.question}")
        for option_index, option in enumerate(item.options):
            label = chr(ord("A") + option_index)
            lines.append(f"  {label}. {option}")
        lines.append(f"A{index}: {item.answer}")
        lines.append(f"Source: {item.source_sentence}")
        lines.append("")
        index += 1
    for item in tf_questions:
        lines.append(f"Q{index}: {item.statement}")
        lines.append(f"A{index}: {item.answer}")
        lines.append(f"Source: {item.source_sentence}")
        lines.append("")
        index += 1
    return "\n".join(lines).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate questions from a book text file."
    )
    parser.add_argument("book", help="Path to the book text file")
    parser.add_argument(
        "--question-type",
        choices=("qa", "mcq", "truefalse", "all"),
        default="qa",
        help="Type of question to generate",
    )
    parser.add_argument(
        "--choices",
        type=int,
        default=4,
        help="Number of options for multiple-choice questions",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for generating choices",
    )
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
    facts = extract_facts(sentences)
    rng = Random(args.seed)
    qa_questions: List[Question] = []
    mcq_questions: List[MultipleChoiceQuestion] = []
    tf_questions: List[TrueFalseQuestion] = []
    if args.question_type in ("qa", "all"):
        qa_questions = generate_qa(facts)
    if args.question_type in ("mcq", "all"):
        mcq_questions = generate_mcq(facts, args.choices, rng)
    if args.question_type in ("truefalse", "all"):
        tf_questions = generate_true_false(facts, rng)
    output = format_output(qa_questions, mcq_questions, tf_questions, args.format)
    print(output)


if __name__ == "__main__":
    main()
