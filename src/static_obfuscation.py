import base64
import logging
import random

logger = logging.getLogger("ObfuscaX")


def insert_junk_code_ps1(script):
    junk_statements = [
        'Write-Verbose "Junk statement..."',
        '$junkVar = Get-Date',
        'Start-Sleep -Milliseconds 10',
        'For ($i=0; $i -lt 5; $i++) { $null = $i }',
        '# Random comment'
    ]
    junk_code = '\n'.join(random.choices(junk_statements, k=3))
    logger.debug("Inserted junk PowerShell code.")
    return junk_code + "\n" + script


def static_obfuscate(payload):
    logger.info("Starting static obfuscation...")
    if isinstance(payload, bytes):
        payload = payload.decode(errors='ignore')

    # -EncodedCommand expects base64 of UTF-16LE, not UTF-8.
    encoded = base64.b64encode(payload.encode("utf-16-le")).decode()
    obf_script = insert_junk_code_ps1(f"powershell -EncodedCommand {encoded}")

    logger.info("Static obfuscation complete.")
    return obf_script.encode()
