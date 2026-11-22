#!/usr/bin/env python3
"""Stamp Cognito configuration into the prebuilt ReLoop frontend bundle.

Copies frontend/dist/ to frontend/build/ and replaces placeholder tokens with
your Cognito User Pool ID, App Client ID, and Managed Login Domain so the
bundle is ready for `aws s3 sync frontend/build/ s3://<web-bucket>/`.
"""

import argparse
import pathlib
import re
import shutil
import sys

POOL_RE = re.compile(r"^[a-z]{2}-[a-z]+-\d+_[A-Za-z0-9]+$")
CLIENT_RE = re.compile(r"^[A-Za-z0-9]{15,64}$")
DOMAIN_RE = re.compile(r"^https://[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

TOKENS = {
    "__COGNITO_USER_POOL_ID__": "pool_id",
    "__COGNITO_CLIENT_ID__": "client_id",
    "__COGNITO_DOMAIN__": "domain",
}


def validate_inputs(pool_id: str, client_id: str, domain: str) -> str:
    clean_domain = domain.strip().rstrip("/")
    if not POOL_RE.match(pool_id):
        raise ValueError(f"Invalid Cognito User Pool ID: {pool_id!r}")
    if not CLIENT_RE.match(client_id):
        raise ValueError(f"Invalid Cognito App Client ID: {client_id!r}")
    if not DOMAIN_RE.match(clean_domain):
        raise ValueError(f"Invalid HTTPS Cognito domain URL: {domain!r}")
    return clean_domain


def configure_bundle(
    src_dir: pathlib.Path,
    out_dir: pathlib.Path,
    pool_id: str,
    client_id: str,
    domain: str,
) -> int:
    clean_domain = validate_inputs(pool_id, client_id, domain)
    if not src_dir.is_dir():
        raise FileNotFoundError(f"Source bundle not found: {src_dir}")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(src_dir, out_dir)

    values = {
        "__COGNITO_USER_POOL_ID__": pool_id,
        "__COGNITO_CLIENT_ID__": client_id,
        "__COGNITO_DOMAIN__": clean_domain,
    }
    found = {k: 0 for k in values}

    for js_file in out_dir.rglob("*.js"):
        text = js_file.read_text(encoding="utf-8")
        changed = False
        for token, replacement in values.items():
            count = text.count(token)
            if count:
                text = text.replace(token, replacement)
                found[token] += count
                changed = True
        if changed:
            js_file.write_text(text, encoding="utf-8")

    missing = [token for token, count in found.items() if count == 0]
    if missing:
        raise RuntimeError(f"Expected placeholder tokens not found in bundle: {missing}")

    return sum(found.values())


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Configure prebuilt ReLoop frontend assets with your Cognito IDs."
    )
    parser.add_argument("--pool-id", required=True, help="Cognito User Pool ID (e.g. ap-southeast-1_abc123)")
    parser.add_argument("--client-id", required=True, help="Cognito App Client ID")
    parser.add_argument(
        "--domain",
        required=True,
        help="Cognito Hosted/Managed Login URL (e.g. https://reloop2-auth.auth.ap-southeast-1.amazoncognito.com)",
    )
    parser.add_argument("--src", type=pathlib.Path, default=here / "dist", help="Template bundle directory")
    parser.add_argument("--out", type=pathlib.Path, default=here / "build", help="Configured output directory")
    args = parser.parse_args()

    try:
        replaced = configure_bundle(args.src, args.out, args.pool_id, args.client_id, args.domain)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Configured {replaced} Cognito tokens in {args.out}")
    print("Next step:")
    print(f"  aws s3 sync {args.out} s3://reloop2-web-<suffix>/ --region ap-southeast-1 --delete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
