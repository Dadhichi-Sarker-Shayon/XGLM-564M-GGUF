<div align="center">

<p>
  <a href="https://huggingface.co/ShayonSarker/xglm-564M-GGUF"><img alt="Hugging Face GGUF" src="https://img.shields.io/badge/Hugging%20Face-GGUF-FFD21E?style=for-the-badge"></a>
  <img alt="XGLM model" src="https://img.shields.io/badge/Model-XGLM--564M-8A2BE2?style=for-the-badge">
  <img alt="GGUF formats" src="https://img.shields.io/badge/GGUF-F16%20%7C%20Q8_0%20%7C%20Q4_K_M-FFD21E?style=for-the-badge">
  <img alt="Languages" src="https://img.shields.io/badge/Languages-30%2B-00A6A6?style=for-the-badge">
  <img alt="Bengali and Bangla" src="https://img.shields.io/badge/Bengali-Bangla-16A34A?style=for-the-badge">
  <img alt="Native llama.cpp" src="https://img.shields.io/badge/llama.cpp-native-24292F?style=for-the-badge">
  <img alt="Validated" src="https://img.shields.io/badge/validated-pass-22C55E?style=for-the-badge">
  <img alt="MIT license" src="https://img.shields.io/badge/License-MIT-7C3AED?style=for-the-badge">
</p>

# 🌍 XGLM-564M GGUF

**Native llama.cpp support and release hub for Meta’s compact multilingual XGLM model.**

🌐 30+ Languages &nbsp;•&nbsp; 🇧🇩 Bengali / Bangla &nbsp;•&nbsp; 🧠 564M Parameters &nbsp;•&nbsp; ⚙️ Native GGUF &nbsp;•&nbsp; ✅ Published

[🚀 Hugging Face Release](https://huggingface.co/ShayonSarker/xglm-564M-GGUF) · [Meta Source Model](https://huggingface.co/facebook/xglm-564M) · [llama.cpp](https://github.com/ggml-org/llama.cpp)

👇 [View verified English and Bangla question/answer examples](#user-content-verified-question-answer-examples)

</div>

---

## ✨ Overview

This repository contains the native `xglm` architecture patch, reproducible setup instructions, a GGUF verifier, and validation results for [`facebook/xglm-564M`](https://huggingface.co/facebook/xglm-564M).

The conversion preserves XGLM’s scaled embeddings, offset sinusoidal positions, biased attention, exact GELU, tied input/output embeddings, and 256,008-token UGM tokenizer.

## 📦 GGUF Formats

The model binaries are hosted on Hugging Face to keep this GitHub repository lightweight.

| Format | Recommended use |
|---|---|
| [`XGLM-564M-F16.gguf`](https://huggingface.co/ShayonSarker/xglm-564M-GGUF/blob/main/XGLM-564M-F16.gguf) | Reference quality |
| [`XGLM-564M-Q8_0.gguf`](https://huggingface.co/ShayonSarker/xglm-564M-GGUF/blob/main/XGLM-564M-Q8_0.gguf) | Strong quality, lower memory |
| [`XGLM-564M-Q4_K_M.gguf`](https://huggingface.co/ShayonSarker/xglm-564M-GGUF/blob/main/XGLM-564M-Q4_K_M.gguf) | Compact local inference |

## 🏗️ Build GGUF End-to-End

`build_gguf.py` clones the pinned llama.cpp commit, applies the native XGLM patch, downloads the pinned Meta checkpoint, creates F16, builds a multilingual importance matrix, creates Q8_0 and Q4_K_M, verifies all three files, and runs a generation smoke test.

```bash
python -m pip install -r requirements-build.txt
python build_gguf.py
python build_gguf.py --dry-run
```

The default build requires at least **8 GB** of free disk space. It writes artifacts to `build-xglm/output/` and does not upload or overwrite the published release.

## 🧩 Apply Patch Manually

```bash
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
git checkout 6b790a9c291b5d7af3312bbf9f0c558aa023b13e
git apply /path/to/this/repository/xglm-llama.cpp.patch
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --target llama-completion
```

The included patch adds:

- `LLM_ARCH_XGLM` runtime support
- Exact-erf GELU
- XGLM embedding scaling
- Native `XGLMForCausalLM` conversion
- XGLM tensor mapping and sinusoidal positions
- XGLM UGM tokenizer metadata

## ✅ Verify a Downloaded GGUF

```bash
python -m pip install -r requirements.txt
python verify_gguf.py /path/to/XGLM-564M-Q4_K_M.gguf
```

The verifier checks architecture, model dimensions, tokenizer settings, embedding scale, and tensor count.

<a id="verified-question-answer-examples"></a>

## ❓ Verified Question → Answer Examples

These are actual Q4_K_M completions at temperature 0. The answers below were fact-checked; incorrect, repetitive, and evasive completions were removed. This curated set is not a benchmark. XGLM is a base model, so the questions are intentionally simple.

| Question | Model answer |
|---|---|
| What is the capital city of Bangladesh? | `Dhaka` |
| What is the capital city of France? | `Paris` |
| Which country has Dhaka as its capital? | `Bangladesh` |
| What gas do humans need to breathe to survive? | `The human body needs oxygen to survive.` |
| What color is the sky on a clear day? | `The sky is blue.` |
| বাংলাদেশের রাজধানী কোন শহর? | `ঢাকা।` |

## 📈 Performance

Lower perplexity (PPL) is better. Scores use separate held-out English and Bengali text with 64-token evaluation windows.

| Format | English PPL | vs F16 | Bengali PPL | vs F16 |
|---|---:|---:|---:|---:|
| F16 | 58.87 | Baseline | 12.15 | Baseline |
| Q8_0 | 59.04 | +0.29% | 12.15 | -0.02% |
| Q4_K_M | 61.44 | +4.37% | 12.66 | +4.21% |

### Validation Summary

- ✅ Token IDs match Transformers across Bengali, English, French, Chinese, and Arabic.
- ✅ F16 output was numerically checked against Transformers.
- ✅ Q8_0 and Q4_K_M pass held-out English and Bengali quality gates.
- ✅ Deterministic English and Bengali generation checks pass.

## 🧩 Intended Use

XGLM-564M is a **base language model**, not an instruction-tuned assistant. It is useful for compact multilingual research, Bengali/English workloads, local generation, and GGUF runtime testing.

Validate important outputs independently. Generated text may be inaccurate or inappropriate.

## 📄 License

MIT. See [`LICENSE`](./LICENSE) and the [upstream model card](https://huggingface.co/facebook/xglm-564M) for source-model attribution.
