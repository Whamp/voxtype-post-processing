from pathlib import Path

from voxtype_post_processing.repair import RepairRequest, repair_text
from voxtype_post_processing.assets import load_asset_bundle


class RecordingLLM:
    def __init__(self, response: str):
        self.response = response
        self.calls = []

    def complete(self, messages, *, max_tokens=None):
        self.calls.append({"messages": messages, "max_tokens": max_tokens})
        return self.response


def test_repair_uses_assets_and_returns_llm_output(tmp_path: Path):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "policy.md").write_text("Use Minimal Accurate Repair.", encoding="utf-8")
    (assets_dir / "system-prompt.md").write_text("Repair dictated text using the assets.", encoding="utf-8")
    (assets_dir / "glossary.md").write_text("- Omarchy\n- LLMs\n- CI/CD\n", encoding="utf-8")
    (assets_dir / "correction-rules.yaml").write_text(
        "rules:\n  - raw: OMACHI\n    repair: Omarchy\n  - raw: LLMMs\n    repair: LLMs\n  - raw: CI CD\n    repair: CI/CD\n",
        encoding="utf-8",
    )
    (assets_dir / "examples.md").write_text(
        "Raw: OMACHI supports LLMMs.\nRepaired: Omarchy supports LLMs.",
        encoding="utf-8",
    )

    llm = RecordingLLM("Omarchy supports LLMs in CI/CD workflows.")

    result = repair_text(
        RepairRequest(raw_text="OMACHI supports LLMMs in CI CD workflows."),
        assets=load_asset_bundle(assets_dir),
        llm=llm,
    )

    assert result.text == "Omarchy supports LLMs in CI/CD workflows."
    assert result.used_fallback is False
    rendered = "\n".join(message["content"] for message in llm.calls[0]["messages"])
    assert "Minimal Accurate Repair" in rendered
    assert "OMACHI" in rendered
    assert "Omarchy" in rendered


def test_repair_falls_back_to_raw_text_when_llm_fails(tmp_path: Path):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "policy.md").write_text("Use Minimal Accurate Repair.", encoding="utf-8")
    (assets_dir / "system-prompt.md").write_text("Repair dictated text.", encoding="utf-8")
    (assets_dir / "glossary.md").write_text("", encoding="utf-8")
    (assets_dir / "correction-rules.yaml").write_text("rules: []\n", encoding="utf-8")
    (assets_dir / "examples.md").write_text("", encoding="utf-8")

    class BrokenLLM:
        def complete(self, messages, *, max_tokens=None):
            raise RuntimeError("server unavailable")

    result = repair_text(
        RepairRequest(raw_text="leave this untouched"),
        assets=load_asset_bundle(assets_dir),
        llm=BrokenLLM(),
    )

    assert result.text == "leave this untouched"
    assert result.used_fallback is True
    assert "server unavailable" in result.error
