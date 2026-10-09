#!/usr/bin/env python3

import argparse
import hashlib
import hmac
import os
import string
import sys
from typing import Optional

CHUNK_SIZE = 1024 * 1024
LABEL_WIDTH = 10
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def eprint(*args):
    """Print to stderr."""
    print(*args, file=sys.stderr)


def paint(text: str, color: str) -> str:
    """Wrap text in an ANSI color only when stdout is a terminal and NO_COLOR is unset."""
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        return text
    return f"{color}{text}{RESET}"


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
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)

    return h.hexdigest()


def normalize_expected_hash(value: str, algorithm: str) -> str:
    """Lowercase and sanity-check an expected hash. Raises ValueError if it can't match."""
    cleaned = value.strip().lower()
    prefix = f"{algorithm}:"
    if cleaned.startswith(prefix):
        cleaned = cleaned[len(prefix):].strip()
    if not cleaned or any(c not in string.hexdigits for c in cleaned):
        raise ValueError("Expected hash must contain only hexadecimal characters (0-9, a-f).")
    expected_len = hashlib.new(algorithm).digest_size * 2
    if len(cleaned) != expected_len:
        raise ValueError(
            f"Expected hash is {len(cleaned)} characters, but {algorithm} produces "
            f"{expected_len}. Check the algorithm and the pasted value."
        )
    return cleaned


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
    value = input(message).strip().lower()
    return value or None


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


def print_fields(**fields: str):
    print()
    for label, value in fields.items():
        print(f"{(label + ':').ljust(LABEL_WIDTH)} {value}")
    print()


def compare_and_report(
    file_path: str, expected_hash: str, algorithm: str, quiet: bool = False
) -> Optional[bool]:
    """Compare hashes and print formatted output. Returns True/False/None for error."""
    if not quiet:
        print()
        print_bunny("Tessa is checking your hash...")
    try:
        actual_hash = compute_hash(file_path, algorithm).lower()
    except OSError as exc:
        eprint(f"Error while computing hash: {exc}")
        return None

    matched = hmac.compare_digest(actual_hash, expected_hash)
    if quiet:
        return matched

    print_fields(
        Algorithm=algorithm, File=file_path, Expected=expected_hash, Actual=actual_hash
    )
    if matched:
        print(f"{paint('[OK]', GREEN)} Hashes match. Integrity verified.\n")
    else:
        print(f"{paint('[FAIL]', RED)} Hash mismatch. File may be corrupted or altered.")
        print("Warning: Hash mismatch detected. Proceed with caution.\n")
    return matched


def generate_and_report(
    file_path: str, algorithm: str, quiet: bool = False
) -> Optional[str]:
    """Generate a hash for the file and print it. Returns hash or None on error."""
    if not quiet:
        print()
        print_bunny("Tessa is generating your hash...")
    try:
        actual_hash = compute_hash(file_path, algorithm).lower()
    except OSError as exc:
        eprint(f"Error while computing hash: {exc}")
        return None

    if quiet:
        print(actual_hash)
    else:
        print_fields(Algorithm=algorithm, File=file_path, Hash=actual_hash)
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

    try:
        expected_hash = normalize_expected_hash(expected_hash, algorithm)
    except ValueError as exc:
        eprint(f"{exc}\n")
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
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="No banner or decoration: print only the hash with --generate, "
             "or nothing when comparing (use the exit code)"
    )
    args = parser.parse_args()

    if not args.file:
        for flag, used in (("--expected", args.expected), ("--generate", args.generate),
                           ("--quiet", args.quiet)):
            if used:
                parser.error(f"{flag} requires --file")
        run_menu()
        return

    if args.generate and args.expected:
        parser.error("--generate and --expected cannot be used together")
    if not args.generate and not args.expected:
        parser.error("--expected is required unless --generate is used")

    file_path = args.file
    if not os.path.isfile(file_path):
        eprint(f"Error: File not found: {file_path}")
        sys.exit(2)

    algorithm = args.algo
    if not args.quiet:
        display_intro()

    if args.generate:
        result = generate_and_report(file_path, algorithm, quiet=args.quiet)
        sys.exit(0 if result is not None else 2)

    try:
        expected_hash = normalize_expected_hash(args.expected, algorithm)
    except ValueError as exc:
        eprint(f"Error: {exc}")
        sys.exit(2)

    result = compare_and_report(file_path, expected_hash, algorithm, quiet=args.quiet)
    if result is None:
        sys.exit(2)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        eprint("\nInterrupted. Goodbye from Tessa the Bun!")
        sys.exit(130)
    except EOFError:
        eprint("\nGoodbye from Tessa the Bun!")
        sys.exit(0)
