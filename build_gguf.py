from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

from pathlib import Path


LLAMA_COMMIT = "6b790a9c291b5d7af3312bbf9f0c558aa023b13e"
MODELS = {
    "facebook/xglm-564M": {
        "revision": "f3059f01b98ccc877c673149e0178c0e957660f9",
        "name": "XGLM-564M",
        "minimum_gb": 8,
    },
    "facebook/xglm-2.9B": {
        "revision": "33c659ae27de09c0a54123d3902dac48cbb8592a",
        "name": "XGLM-2.9B",
        "minimum_gb": 30,
    },
}
DOWNLOAD_PATTERNS = [
    "config.json",
    "generation_config.json",
    "pytorch_model.bin",
    "sentencepiece.bpe.model",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
]
CALIBRATION = """XGLM is a multilingual language model developed for broad language understanding and generation. It was trained on text from many languages, including Bengali, English, French, German, Arabic, Russian, Chinese, Japanese, Spanish, Portuguese, Hindi, and Turkish. The same model can process prompts in these languages because its vocabulary and training data are intentionally multilingual.

The capital of France is Paris. The capital of Bangladesh is Dhaka. বাংলাদেশের রাজধানী ঢাকা। ঢাকা নদীর পাড়ে অবস্থিত এবং এটি বাংলাদেশের রাজনৈতিক, অর্থনৈতিক ও সাংস্কৃতিক কেন্দ্র।

Les systèmes d’apprentissage automatique utilisent des exemples pour apprendre des relations. Machine learning systems should be evaluated with data that was not used for training. A model should perform consistently across languages instead of memorizing a small benchmark.

Los sistemas de aprendizaje automático aprenden patrones a partir de ejemplos. La evaluación debe utilizar datos que no se hayan usado durante el entrenamiento. El rendimiento debería ser estable en español, inglés y otras lenguas.

機械学習系统在测试时应该使用没有出现在训练数据中的样本。異なる言語でも安定した性能を確認することが重要です。Разные языки должны сохранять качество модели. नमूना जांच में प्रशिक्षण से अलग डेटा का उपयोग किया जाना चाहिए।
"""


def run(command, cwd=None):
    print("+", " ".join(str(part) for part in command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def output(command, cwd=None):
    return subprocess.check_output(command, cwd=cwd, text=True).strip()


def ensure_llama_cpp(repo_root, work_dir):
    llama_dir = work_dir / "llama.cpp"
    patch = repo_root / "xglm-llama.cpp.patch"
    if not (llama_dir / ".git").is_dir():
        llama_dir.mkdir(parents=True)
        run(["git", "init"], llama_dir)
    if subprocess.run(["git", "remote", "get-url", "origin"], cwd=llama_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        run(["git", "remote", "add", "origin", "https://github.com/ggml-org/llama.cpp.git"], llama_dir)
    head_result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=llama_dir, capture_output=True, text=True)
    head = head_result.stdout.strip() if head_result.returncode == 0 else ""
    if head != LLAMA_COMMIT:
        if output(["git", "status", "--porcelain"], llama_dir):
            raise RuntimeError("The llama.cpp work directory has unrelated changes")
        run(["git", "fetch", "--depth", "1", "origin", LLAMA_COMMIT], llama_dir)
        run(["git", "checkout", "--detach", LLAMA_COMMIT], llama_dir)
    reverse = subprocess.run(
        ["git", "apply", "--reverse", "--check", str(patch)],
        cwd=llama_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if reverse.returncode != 0:
        if output(["git", "status", "--porcelain"], llama_dir):
            raise RuntimeError("The llama.cpp work directory has unrelated changes")
        run(["git", "apply", str(patch)], llama_dir)
    return llama_dir


def find_executable(build_dir, name):
    candidates = [
        build_dir / "bin" / name,
        build_dir / "bin" / "Release" / f"{name}.exe",
        build_dir / f"{name}.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", choices=sorted(MODELS), default="facebook/xglm-564M")
    parser.add_argument("--work-dir", type=Path, default=Path("build-xglm"))
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = MODELS[args.model_id]
    repo_root = Path(__file__).resolve().parent
    work_dir = args.work_dir.resolve()
    source_dir = work_dir / args.model_id.split("/")[-1]
    output_dir = work_dir / "output"
    llama_dir = work_dir / "llama.cpp"
    build_dir = llama_dir / "build"
    f16 = output_dir / f"{config['name']}-F16.gguf"
    q8 = output_dir / f"{config['name']}-Q8_0.gguf"
    q4 = output_dir / f"{config['name']}-Q4_K_M.gguf"

    if args.dry_run:
        print(json.dumps({
            "model_id": args.model_id,
            "revision": config["revision"],
            "name": config["name"],
            "minimum_free_gb": config["minimum_gb"],
            "work_dir": str(work_dir),
            "patches": str(repo_root / "xglm-llama.cpp.patch"),
            "outputs": [str(f16), str(q8), str(q4)],
        }, indent=2))
        return

    if args.threads < 1:
        raise ValueError("--threads must be positive")
    if not shutil.which("git") or not shutil.which("cmake"):
        raise RuntimeError("git and cmake are required")
    from huggingface_hub import snapshot_download

    work_dir.mkdir(parents=True, exist_ok=True)
    free_gb = shutil.disk_usage(work_dir).free / 1_000_000_000
    if free_gb < config["minimum_gb"]:
        raise RuntimeError(f"At least {config['minimum_gb']} GB of free space is required; found {free_gb:.1f} GB")

    snapshot_download(
        repo_id=args.model_id,
        revision=config["revision"],
        local_dir=source_dir,
        allow_patterns=DOWNLOAD_PATTERNS,
    )

    llama_dir = ensure_llama_cpp(repo_root, work_dir)
    run([
        "cmake", "-S", str(llama_dir), "-B", str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DGGML_NATIVE=ON",
        "-DLLAMA_CURL=OFF",
        "-DLLAMA_BUILD_TESTS=OFF",
        "-DLLAMA_BUILD_SERVER=OFF",
    ])
    run([
        "cmake", "--build", str(build_dir), "--config", "Release",
        "--target", "llama-quantize", "llama-imatrix", "llama-completion",
        "--parallel", str(args.threads),
    ])

    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = output_dir / "metadata.json"
    metadata.write_text(json.dumps({
        "general.name": config["name"],
        "general.finetune": None,
        "general.author": "Meta",
        "general.organization": "Meta",
        "general.license.name": "MIT",
        "general.license.link": f"https://huggingface.co/{args.model_id}",
        "general.source.url": f"https://huggingface.co/{args.model_id}",
        "general.source.repo_url": f"https://huggingface.co/{args.model_id}",
    }, indent=2), encoding="utf-8")

    calibration = output_dir / "calibration.txt"
    calibration.write_text(CALIBRATION, encoding="utf-8")
    imatrix = output_dir / "multilingual.imatrix.gguf"

    run([
        sys.executable, str(llama_dir / "convert_hf_to_gguf.py"),
        str(source_dir), "--outfile", str(f16),
        "--outtype", "f16", "--metadata", str(metadata),
    ])
    run([
        str(find_executable(build_dir, "llama-imatrix")),
        "-m", str(f16), "-f", str(calibration),
        "-c", "64", "-b", "64", "--chunks", "2",
        "-ngl", "0", "-t", str(args.threads), "--process-output",
        "-o", str(imatrix),
    ])
    quantize = str(find_executable(build_dir, "llama-quantize"))
    run([quantize, str(f16), str(q8), "Q8_0", str(args.threads)])
    run([quantize, "--imatrix", str(imatrix), str(f16), str(q4), "Q4_K_M", str(args.threads)])

    verify = str(repo_root / "verify_gguf.py")
    for model in (f16, q8, q4):
        run([sys.executable, verify, str(model)])

    run([
        str(find_executable(build_dir, "llama-completion")),
        "-m", str(q4), "-p", "The capital of France is",
        "-n", "8", "--temp", "0", "-ngl", "0",
        "-t", str(args.threads), "-c", "64",
    ])
    print(f"Completed: {output_dir}")


if __name__ == "__main__":
    main()
