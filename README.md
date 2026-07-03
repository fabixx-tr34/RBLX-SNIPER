# RBLX-Sniper

Roblox name generator + checker

A multithreaded Python tool that generates random usernames and checks their availability on Roblox in real time.

## Features

- Generates random usernames with a custom length (1-20 characters)
- Checks availability using Roblox's official validation endpoint
- Multithreaded checking for faster results
- Pause / resume anytime with the `P` key
- Change username length on the fly while paused
- Valid usernames are automatically saved to `hits.txt`
- Simple color-coded console output (valid, taken, censored, unknown)

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python RBLX SNIPER.py
```

Or just run `setup.bat` on Windows, it installs the dependencies and launches the program automatically.

## Controls

| Key | Action |
|-----|--------|
| `P` | Pause / Resume the checker |

While paused, you can choose to change the username length before resuming.

## Output

Every available username found gets saved to `hits.txt` in the same folder.

## License

This project is licensed under the MIT License.

---

made by: [fabixx-tr34](https://github.com/fabixx-tr34)
