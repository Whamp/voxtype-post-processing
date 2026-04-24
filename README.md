# voxtype-post-processing

Minimal Accurate Repair for Voxtype post-processing.

This repo owns the repair behavior and editable assets used after Voxtype has produced a raw transcription and before Voxtype outputs text into the active application.

## Current v1 shape

- Reads raw transcription from `stdin`.
- Uses editable repair assets from `assets/default/`.
- Calls an OpenAI-compatible chat completion endpoint.
- Writes insertion-ready repaired text to `stdout`.
- Falls back to the original raw transcription on failure.
- Records repair observations in local SQLite when enabled by the CLI default.

## LLM endpoint configuration

The CLI calls an OpenAI-compatible chat completion endpoint. Public defaults are intentionally generic; configure your personal endpoint locally with environment variables instead of committing it:

```bash
export VOXTYPE_LLM_BASE_URL="http://localhost:8000/v1"
export VOXTYPE_LLM_MODEL="your-local-model"
```

## Manual test

```bash
printf 'Our current environment is OMACHI and post-processing using LLMMs is possible for CI CD workflows.' \
  | uv run voxtype-post-process
```
