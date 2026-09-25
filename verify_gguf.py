import argparse

from gguf import GGUFReader


EXPECTED = {
    "general.architecture": "xglm",
    "general.name": "XGLM-564M",
    "xglm.block_count": 24,
    "xglm.context_length": 2048,
    "xglm.embedding_length": 1024,
    "xglm.feed_forward_length": 4096,
    "xglm.attention.head_count": 16,
    "xglm.embedding_scale": 32.0,
    "tokenizer.ggml.model": "t5",
    "tokenizer.ggml.bos_token_id": 2,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=str)
    args = parser.parse_args()

    reader = GGUFReader(args.model)
    errors = []

    for key, expected in EXPECTED.items():
        field = reader.get_field(key)
        actual = field.contents() if field is not None else None
        valid = actual is not None
        if valid and isinstance(expected, float):
            valid = abs(float(actual) - expected) < 1e-4
        else:
            valid = actual == expected
        print(f"{key}: {actual}")
        if not valid:
            errors.append(f"{key}: expected {expected!r}, got {actual!r}")

    tensor_count = len(reader.tensors)
    print(f"tensor_count: {tensor_count}")
    if tensor_count != 292:
        errors.append(f"tensor_count: expected 292, got {tensor_count}")

    if errors:
        raise SystemExit("GGUF verification failed:\n" + "\n".join(errors))

    print("GGUF verification passed")


if __name__ == "__main__":
    main()
