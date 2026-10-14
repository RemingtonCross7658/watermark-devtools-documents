"""Runnable command for a single developer-document release."""

import argparse
import json

from watermark_service import InfraiClient, prepare_release


def main() -> None:
    parser = argparse.ArgumentParser(description="Watermark one PDF before sharing")
    parser.add_argument("document_name")
    parser.add_argument("pdf")
    parser.add_argument("--external", action="store_true")
    args = parser.parse_args()
    result = prepare_release(InfraiClient(), args.document_name, args.pdf, args.external)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
