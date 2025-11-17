#!/usr/bin/env python3

import argparse
import hashlib
import os
import sys
from typing import Optional

CHUNK_SIZE = 8192
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


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


def display_intro():
    print("")  # blank line before banner for readability
    logo_lines = [
        "░▀█▀░█▀▀░█▀▀░█▀▀░█▀█",
        "░░█░░█▀▀░▀▀█░▀▀█░█▀█",
        "░░▀░░▀▀▀░▀▀▀░▀▀▀░▀░▀",
    ]
    bunny_lines = _bunny_lines("Ready to hop into hashing!")
    for logo_line, bunny_line in zip(logo_lines, bunny_lines):
        print(f"{logo_line}   {bunny_line}")
    print("\nTESSA THE HASH-BUN v0.1\n")


def _bunny_lines(status: str) -> list[str]:
    message = status or "Tessa says hello!"
    return [
        "  (\\_/)",
        f" (='.'=)  {message}",
        " (\")_(\")",
    ]


def print_bunny(status: str = ""):
    """Render a monospaced-friendly bunny with a status message."""
    print("\n".join(_bunny_lines(status or "Tessa says hello!")))


def prompt_existing_file(message: str) -> Optional[str]:
    while True:
        path = input(message).strip()
        if not path:
            return None
        if os.path.isfile(path):
            return path
        print("File not found. Please try again or press Enter to return to the menu.")


def prompt_expected_hash(message: str) -> Optional[str]:
    while True:
        value = input(message).strip().lower()
        if not value:
            return None
        return value


def prompt_algorithm(default: str = "sha256") -> Optional[str]:
    popular = ("md5", "sha256", "sha512", "blake2b", "sha1")
    popular_supported = [algo.upper() for algo in popular if algo in SUPPORTED_ALGORITHMS]
    preview = ", ".join(popular_supported[:5])
    prompt = (
        f"Hash algorithm (Enter={default}. Popular: [{preview}] "
        "or 'back' to return): "
    )
    while True:
        algo = input(prompt).strip().lower()
        if not algo:
            return default
        if algo == "back":
            return None
        if algo == "default":
            algo = default
        if algo in SUPPORTED_ALGORITHMS:
            return algo
        print("Unsupported algorithm. Try again.")


def compare_and_report(file_path: str, expected_hash: str, algorithm: str) -> Optional[bool]:
    """Compare hashes and print formatted output. Returns True/False/None for error."""
    print()
    print_bunny("Tessa is checking your hash...")
    try:
        actual_hash = compute_hash(file_path, algorithm).lower()
    except Exception as exc:
        print(f"Error while computing hash: {exc}")
        return None

    label_width = 10
    print("")
    print(f"{'Algorithm:'.ljust(label_width)} {algorithm}")
    print(f"{'File:'.ljust(label_width)} {file_path}")
    print(f"{'Expected:'.ljust(label_width)} {expected_hash}")
    print(f"{'Actual:'.ljust(label_width)} {actual_hash}\n")

    if actual_hash == expected_hash:
        print(f"{GREEN}[OK]{RESET} Hashes match. Integrity verified.\n")
        return True
    else:
        print(f"{RED}[FAIL]{RESET} Hash mismatch. File may be corrupted or altered.")
        print("Warning: Hash mismatch detected. Proceed with caution.\n")
        return False


def generate_and_report(file_path: str, algorithm: str) -> Optional[str]:
    """Generate a hash for the file and print it. Returns hash or None on error."""
    print()
    print_bunny("Tessa is generating your hash...")
    print()
    try:
        actual_hash = compute_hash(file_path, algorithm).lower()
    except Exception as exc:
        print(f"Error while computing hash: {exc}")
        return None

    label_width = 10
    print("")
    print(f"{'Algorithm:'.ljust(label_width)} {algorithm}")
    print(f"{'File:'.ljust(label_width)} {file_path}")
    print(f"{'Hash:'.ljust(label_width)} {actual_hash}\n")
    return actual_hash


def compare_hashes():
    print("\n== Compare Hashes ==")
    file_path = prompt_existing_file(
        "Enter the path to the file (press Enter to return): "
    )
    if file_path is None:
        print("No file selected. Returning to the main menu.\n")
        return

    expected_hash = prompt_expected_hash(
        "Enter the expected hash (press Enter to return): "
    )
    if expected_hash is None:
        print("No expected hash entered. Returning to the main menu.\n")
        return

    algorithm = prompt_algorithm()
    if algorithm is None:
        print("No algorithm selected. Returning to the main menu.\n")
        return

    compare_and_report(file_path, expected_hash, algorithm)


def generate_hash():
    print("\n== Generate Hash ==")
    file_path = prompt_existing_file(
        "Enter the path to the file (press Enter to return): "
    )
    if file_path is None:
        print("No file selected. Returning to the main menu.\n")
        return

    algorithm = prompt_algorithm()
    if algorithm is None:
        print("No algorithm selected. Returning to the main menu.\n")
        return

    generate_and_report(file_path, algorithm)


def run_menu():
    display_intro()
    while True:
        print("Choose an option:")
        print("  1. Compare hashes")
        print("  2. Generate hash")
        print("  3. Exit")
        choice = input("Selection: ").strip()
        if choice == "1":
            compare_hashes()
        elif choice == "2":
            generate_hash()
        elif choice == "3":
            print("Goodbye from Tessa the Bun!")
            break
        else:
            print("Invalid selection. Please choose 1, 2, or 3.")


def main():
    parser = argparse.ArgumentParser(
        description="Tessa the Bun - friendly file hashing companion"
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to the file you want to hash (enables non-interactive mode)"
    )
    parser.add_argument(
        "-e", "--expected",
        help="Expected hash value when comparing"
    )
    parser.add_argument(
        "-a", "--algo",
        default="sha256",
        type=str.lower,
        choices=SUPPORTED_ALGORITHMS,
        help="Hash algorithm to use (default: sha256)"
    )
    parser.add_argument(
        "-g", "--generate",
        action="store_true",
        help="Generate a hash instead of comparing when using --file"
    )
    args = parser.parse_args()

    if args.file:
        file_path = args.file
        if not os.path.isfile(file_path):
            print(f"Error: File not found: {file_path}")
            sys.exit(2)

        algorithm = args.algo
        display_intro()
        if args.generate:
            result = generate_and_report(file_path, algorithm)
            sys.exit(0 if result is not None else 2)

        if not args.expected:
            print("Error: --expected is required unless --generate is used.")
            sys.exit(2)

        expected_hash = args.expected.strip().lower()
        result = compare_and_report(file_path, expected_hash, algorithm)
        if result is None:
            sys.exit(2)
        sys.exit(0 if result else 1)

    run_menu()

if __name__ == "__main__":
    main()
