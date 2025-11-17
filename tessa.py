#!/usr/bin/env python3

import argparse
import hashlib
import os
import sys

CHUNK_SIZE = 8192


def _fixed_digest_algorithms():
    """Filter out algorithms that require an explicit digest length."""
    fixed = set()
    for name in hashlib.algorithms_available:
        candidate = name.lower()
        if candidate in fixed:
            continue
        try:
            hashlib.new(candidate).hexdigest()
        except (TypeError, ValueError):
            continue
        fixed.add(candidate)
    return tuple(sorted(fixed))


SUPPORTED_ALGORITHMS = _fixed_digest_algorithms()


def print_bunny():
    bunny = r"""
 (\_/)
 ( ^_^)
 / >🥕   Tessa is checking your file...
"""
    print(bunny)


def compute_hash(file_path: str, algorithm: str) -> str:
    """Compute hash of a file using the chosen algorithm."""
    try:
        h = hashlib.new(algorithm)
    except ValueError:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description="Tessa - Simple file hash verification tool"
    )

    parser.add_argument(
        "--file", "-f",
        required=True,
        help="Path to the file you want to hash"
    )

    parser.add_argument(
        "--expected", "-e",
        required=True,
        help="Expected hash value from the developer"
    )

    parser.add_argument(
        "--algo", "-a",
        default="sha256",
        type=str.lower,
        choices=SUPPORTED_ALGORITHMS,
        help="Hash algorithm to use (default: sha256)"
    )

    args = parser.parse_args()

    print_bunny()

    file_path = args.file
    expected_hash = args.expected.strip().lower()
    algo = args.algo

    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(2)

    try:
        actual_hash = compute_hash(file_path, algo)
    except Exception as e:
        print(f"Error: Could not compute hash: {e}")
        sys.exit(2)

    actual_hash = actual_hash.lower()

    print(f"Algorithm: {algo}")
    print(f"File: {file_path}")
    print(f"Expected: {expected_hash}")
    print(f"Actual:   {actual_hash}")
    print("")

    if actual_hash == expected_hash:
        print("[OK] Hashes match. Integrity verified.")
        sys.exit(0)
    else:
        print("[FAIL] Hash mismatch. File may be corrupted or altered.")
        sys.exit(1)


if __name__ == "__main__":
    main()
