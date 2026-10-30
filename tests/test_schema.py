import pytest

from builder.validate import schema_errors


def test_good_generated_file_is_valid(good_generated):
    assert schema_errors("generated", good_generated, "t") == []


@pytest.mark.parametrize("mutate, needle", [
    (lambda d: d["questions"][0]["explanations"].pop("B"), "'B' is a required property"),
    (lambda d: d["questions"][0].pop("calc"), "'calc' is a required property"),
    (lambda d: d["questions"][0].update(options=["a", "b"]), "too short"),
    (lambda d: d["questions"][0].update(difficulty=4), "4 is not one of"),
    (lambda d: d["connections"][0].update(type="related"), "is not one of"),
    (lambda d: d["questions"][0].update(los="los.1.c"), "does not match"),
    (lambda d: d["repairs"].update({"fig.0123456789": {"kind": "table"}}), "'rows' is a required property"),
    (lambda d: d["learning"]["logic_chain"].pop(), "is too short"),
])
def test_bad_generated_file_is_rejected(good_generated, mutate, needle):
    doc = good_generated
    mutate(doc)
    errors = schema_errors("generated", doc, "t")
    assert errors and any(needle in e["msg"] for e in errors), errors


def test_event_schema():
    ev = {"id": "0190a1b2-0000-7000-8000-000000000000", "v": 1, "device": "laptop", "ts": 1730000000000,
          "type": "answer", "payload": {"qid": "q.01.c.001", "los": ["los.01.c"], "topic": "quant", "correct": True,
                                        "ms": 95000, "confidence": 2, "mode": "drill", "choice": "A"}}
    assert schema_errors("event", ev, "e") == []
    ev["payload"]["confidence"] = 5
    assert schema_errors("event", ev, "e")


def test_content_lint_catches_miskeyed_and_thin_explanations(good_generated):
    from builder.validate import _lint_question
    q = good_generated["questions"][0]
    assert _lint_question(q, "t") == []
    q["answer"] = "B"  # explanations still say A is correct
    codes = [i["code"] for i in _lint_question(q, "t")]
    assert codes.count("answer_key_mismatch") == 2
    q["answer"], q["explanations"]["C"] = "A", "Wrong."
    assert [i["code"] for i in _lint_question(q, "t")] == ["thin_explanation"]
    q["explanations"]["C"], q["options"][2] = "Wrong. Sign error.", "0.596"
    assert [i["code"] for i in _lint_question(q, "t")] == ["duplicate_options"]
