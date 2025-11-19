# Tessa the Hash-Bun

```
░▀█▀░█▀▀░█▀▀░█▀▀░█▀█   (\_/)
░░█░░█▀▀░▀▀█░▀▀█░█▀█  (='.'=)  Ready to hop into hashing!
░░▀░░▀▀▀░▀▀▀░▀▀▀░▀░▀  (")_(")
                       
```

Tessa is a cheerful command-line companion for validating file integrity. Feed her a file and she will generate or compare cryptographic hashes, let you know if everything matches, and throw in a supportive bunny for good measure.

## Features

- Friendly interactive menu for comparing and generating hashes without memorizing flags.
- Fully scripted mode for automation via `--file`, `--expected`, `--algo`, and `--generate` flags.
- Color-coded verdicts so matching hashes pop in green and mismatches warn in red.
- Supports every fixed-length algorithm exposed by your local `hashlib` (SHA variants, MD5, BLAKE2, etc.).
- Cozy ASCII branding so even checksum chores feel welcoming.

## Getting Started

1. Clone the repository and move into it:
   ```bash
   git clone <repo-url> && cd tessa
   ```
2. Ensure you are using Python 3.9+ with standard library `hashlib`.
3. Run `python3 tessa.py` to let Tessa hop into action.

## Usage

### Interactive mode

```
python3 tessa.py
```

Follow the prompts to pick a file, choose a hash algorithm (defaults to SHA-256), and either verify an expected hash or generate a new one.

### Scriptable mode

Compare a file’s hash against a known value:

```
python3 tessa.py --file /path/to/file.iso --expected 123abc... --algo sha256
```

Generate a hash directly:

```
python3 tessa.py --file /path/to/file.iso --generate --algo blake2b
```

Exit codes follow Unix conventions (`0` = success or generated hash, `1` = mismatch, `2` = error) so you can slot Tessa into CI pipelines or install scripts.

## Inspiration

Checksum utilities can feel stern; Tessa keeps the security benefits while adding warmth. Whether you are double-checking a download or cataloging backups, let the Hash-Bun keep watch. 🐰
