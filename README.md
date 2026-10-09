# Tessa the Hash-Bun

```
░▀█▀░█▀▀░█▀▀░█▀▀░█▀█   (\_/)
░░█░░█▀▀░▀▀█░▀▀█░█▀█  (='.'=)  Ready to hop into hashing!
░░▀░░▀▀▀░▀▀▀░▀▀▀░▀░▀  (")_(")
```

Tessa is a friendly command-line tool for checking file integrity. Give her a file and she will generate its hash or compare it against one you already have, then tell you whether it matches. She is a single Python file with no dependencies.

## Features

- Interactive menu for comparing and generating hashes, no flags to memorize.
- Scriptable mode with clear exit codes for CI and install scripts.
- Supports every fixed-length algorithm in your local `hashlib` (SHA-2, SHA-3, BLAKE2, MD5, and more).
- Validates the expected hash before comparing, so a bad paste is reported as bad input, not as a corrupted file.
- Color output only on a terminal, and `NO_COLOR` is respected.

## Quick start

Requires Python 3.9 or newer.

```bash
git clone https://github.com/manipulates/tessa.git
cd tessa
python3 tessa.py
```

## Usage

### Interactive mode

```bash
python3 tessa.py
```

Pick **Compare** or **Generate**, enter a file path, and choose an algorithm (SHA-256 by default). Press Enter at any prompt to go back to the menu.

### Command-line mode

Passing `--file` skips the menu.

Compare a file against a known hash:

```bash
python3 tessa.py --file ubuntu.iso --expected 123abc... --algo sha256
```

Generate a hash:

```bash
python3 tessa.py --file ubuntu.iso --generate --algo blake2b
```

Use it in a script:

```bash
# Print only the hash
HASH=$(python3 tessa.py -f ubuntu.iso -g -q)

# Verify silently and branch on the exit code
if python3 tessa.py -f ubuntu.iso -e "$EXPECTED" -q; then
  echo "verified"
fi
```

### Options

| Option | Description |
| --- | --- |
| `-f`, `--file FILE` | File to hash. Enables command-line mode. |
| `-e`, `--expected HASH` | Expected hash to compare against. An `algo:` prefix such as `sha256:...` is accepted. |
| `-a`, `--algo ALGO` | Hash algorithm (default `sha256`). |
| `-g`, `--generate` | Print the file's hash instead of comparing. Cannot be combined with `--expected`. |
| `-q`, `--quiet` | No banner. Prints only the hash with `--generate`, and nothing when comparing. |
| `-h`, `--help` | Show help, including the full algorithm list. |

`--expected`, `--generate` and `--quiet` all require `--file`.

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Hashes match, or a hash was generated. |
| `1` | Hashes do not match. |
| `2` | Error: missing file, unreadable file, malformed expected hash, or invalid flags. |
| `130` | Interrupted with Ctrl-C. |

## Development

Run the tests (standard library only, nothing to install):

```bash
python3 -m unittest discover -s tests
```

## Why Tessa?

Checksum tools can feel stern. Tessa keeps the security benefits and adds some warmth. Whether you are double-checking a download or cataloging backups, let the Hash-Bun keep watch. 🐰
