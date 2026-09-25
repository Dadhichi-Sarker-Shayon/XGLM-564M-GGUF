---
license: mit
base_model: facebook/xglm-564M
tags:
  - gguf
  - xglm
  - multilingual
  - bengali
  - bangla
  - text-generation
language:
  - bn
  - en
  - fr
  - de
  - ar
  - ru
  - zh
  - ja
  - es
---

<div align="center">

<p>
  <a href="https://huggingface.co/ShayonSarker/xglm-564M-GGUF"><img alt="Hugging Face GGUF" src="https://img.shields.io/badge/Hugging%20Face-GGUF-FFD21E?style=for-the-badge"></a>
  <img alt="XGLM model" src="https://img.shields.io/badge/Model-XGLM--564M-8A2BE2?style=for-the-badge">
  <img alt="GGUF formats" src="https://img.shields.io/badge/GGUF-F16%20%7C%20Q8_0%20%7C%20Q4_K_M-FFD21E?style=for-the-badge">
  <img alt="Languages" src="https://img.shields.io/badge/Languages-30%2B-00A6A6?style=for-the-badge">
  <img alt="Bengali and Bangla" src="https://img.shields.io/badge/Bengali-Bangla-16A34A?style=for-the-badge">
  <img alt="Runtime" src="https://img.shields.io/badge/runtime-llama.cpp%20%2B%20patch-E8590C?style=for-the-badge">
  <img alt="Validated" src="https://img.shields.io/badge/validated-pass-22C55E?style=for-the-badge">
  <img alt="MIT license" src="https://img.shields.io/badge/License-MIT-7C3AED?style=for-the-badge">
</p>

# 🌍 XGLM-564M GGUF

**A compact multilingual base model for Bengali, English, and global language workloads.**

🌐 30+ Languages &nbsp;•&nbsp; 🇧🇩 Bengali / Bangla &nbsp;•&nbsp; 🧠 Base Model &nbsp;•&nbsp; ⚙️ GGUF (llama.cpp + patch) &nbsp;•&nbsp; 📦 564M Parameters &nbsp;•&nbsp; ⚖️ MIT

[Source model](https://huggingface.co/facebook/xglm-564M) · [llama.cpp](https://github.com/ggml-org/llama.cpp)

👇 [View verified English and Bangla question/answer examples](#verified-question-answer-examples)

</div>

---

## ✨ Highlights

- XGLM support for [llama.cpp](https://github.com/ggml-org/llama.cpp) via the included `xglm-llama.cpp.patch` (upstream does not ship this architecture)
- 256,008-token vocabulary with verified multilingual token parity
- 2,048-token context window
- F16, Q8_0, and importance-matrix-calibrated Q4_K_M formats

## 📦 Choose a Format

| File | Status | Best for |
|---|---|---|
| `XGLM-564M-F16.gguf` | Published | Reference quality and maximum fidelity |
| `XGLM-564M-Q8_0.gguf` | Published | Strong quality with a smaller memory footprint |
| `XGLM-564M-Q4_K_M.gguf` | Published | Compact local deployment |

## ⚠️ Runtime requirement

Stock `llama.cpp` **cannot load these files** and fails with `unknown model architecture: 'xglm'`. XGLM is not in upstream llama.cpp. Apply the bundled patch against the pinned commit:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
git checkout 6b790a9c291b5d7af3312bbf9f0c558aa023b13e
git apply /path/to/xglm-llama.cpp.patch
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --target llama-completion
```

Alternatives that need no patch: `transformers` with `facebook/xglm-564M`, or the HF `gguf` file with a runtime that implements `xglm`.

## 🏗️ Rebuild

The [GitHub release hub](https://github.com/Dadhichi-Sarker-Shayon/XGLM-564M-GGUF) includes the end-to-end builder, XGLM runtime patch, verifier, and pinned dependencies.

```bash
git clone https://github.com/Dadhichi-Sarker-Shayon/XGLM-564M-GGUF.git
cd XGLM-564M-GGUF
python -m pip install -r requirements-build.txt
python build_gguf.py
```

The build requires at least **8 GB** of free disk space. It does not overwrite this release.

## 🚀 Run Locally

Apply the [runtime patch](#-runtime-requirement) first, then:

```bash
hf download ShayonSarker/xglm-564M-GGUF XGLM-564M-Q4_K_M.gguf --local-dir .

llama-completion -m ./XGLM-564M-Q4_K_M.gguf \
  -p "Question: What is the capital of Japan?
Answer:" \
  -n 24 --temp 0
```

Expected output: `The capital of Japan is Tokyo.`

<a id="verified-question-answer-examples"></a>

## ❓ Verified Question → Answer Examples

Every row below is a verbatim `XGLM-564M-Q4_K_M.gguf` completion produced with the patched build at `--temp 0`, 24 new tokens, prompt form `Question: ...\nAnswer:`. Nothing is hand-written; rows that came out wrong are moved to the failure table below instead of being edited into looking correct. This is a smoke test, not a benchmark.

| Question | Model answer (verbatim) |
|---|---|
| What is the capital of Japan? | `The capital of Japan is Tokyo.` |
| What is the capital of Italy? | `The capital of Italy is Rome.` |
| What is the capital of Egypt? | `The capital of Egypt is Cairo.` |
| What is the largest ocean on Earth? | `The largest ocean on Earth is the Pacific Ocean.` |

## ⚠️ Known Failures

A 564M-parameter base model is not a fact database. The same settings that produced the table above also produced these, published here so the ceiling is visible:

| Question | Model answer (verbatim) |
|---|---|
| Which planet is closest to the Sun? | `The Sun is located in the constellation of the Sun.` |
| How many days are in a leap year? | `The leap year is the time in which the Earth is in a constant state of motion.` |
| How many continents are there? | `There are approximately 6,000 continents in the world.` |
| What is the chemical symbol for gold? | `The chemical symbol for gold is the symbol of the gold-rich element, the gold-rich element is the symbol of` |
| জাপানের রাজধানী কোন শহর? | `মালয়েশিয়া।` |
| সোনার রাসায়নিক প্রতীক কী? | `সোনার রাসায়নিক প্রতীক হল লোহা, লোহা হল লোহা, লোহা` |

Bengali/Bangla prompting on this checkpoint is unreliable. Use the 2.9B release for Bangla work, and expect factual errors from either model outside simple lookups.

## 📈 Performance

Lower perplexity (PPL) is better. Scores use separate held-out English and Bengali text with 64-token evaluation windows.

| Format | English PPL | vs F16 | Bengali PPL | vs F16 |
|---|---:|---:|---:|---:|
| F16 | 58.87 | Baseline | 12.15 | Baseline |
| Q8_0 | 59.04 | +0.29% | 12.15 | -0.02% |
| Q4_K_M | 61.44 | +4.37% | 12.66 | +4.21% |

## 🔬 Validation

- Token IDs match Transformers across Bengali, English, French, Chinese, and Arabic.
- F16 output was numerically checked against Transformers.
- Both quantized formats pass the English and Bengali quality gates.

## 🧩 Intended Use

XGLM-564M is a **base language model**, not an instruction-tuned assistant. It is suitable for compact multilingual research, Bengali/English experiments, local generation, and GGUF runtime testing.

Outputs may be inaccurate or inappropriate. Validate important results independently.

## 📄 License

MIT. See the [upstream model card](https://huggingface.co/facebook/xglm-564M) for source-model details and attribution.
