"""CLI: python -m mini_fuzz fuzz ... oder python -m mini_fuzz replay ..."""

import argparse
import sys
from pathlib import Path

from .engine import run_fuzzer
from .protocol import InvalidMessage, parse_buggy, parse_fixed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m mini_fuzz", description="Kleines Fuzzing-Labor für Python"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    fuzz = commands.add_parser("fuzz", help="Testeingaben erzeugen und Parser prüfen")
    fuzz.add_argument("--target", choices=("buggy", "fixed"), default="buggy")
    fuzz.add_argument("--iterations", type=int, default=2000)
    fuzz.add_argument("--seed", type=int, default=42)
    fuzz.add_argument("--out", type=Path, default=Path("crashes"))
    fuzz.add_argument("--max-crashes", type=int, default=3)

    manual = commands.add_parser("test", help="Eigene Nachrichten manuell testen")
    manual.add_argument("message", nargs="?", help="Nachricht, z. B. MSG|alice|Hallo")

    replay = commands.add_parser("replay", help="Gespeicherten Crash erneut untersuchen")
    replay.add_argument("path", type=Path)

    args = parser.parse_args(argv)
    if args.command == "fuzz":
        target = parse_buggy if args.target == "buggy" else parse_fixed
        try:
            report = run_fuzzer(
                target,
                iterations=args.iterations,
                seed=args.seed,
                out_dir=args.out,
                max_crashes=args.max_crashes,
            )
        except ValueError as exc:
            parser.error(str(exc))

        print(f"Target: {args.target} | Seed: {args.seed}")
        print(f"Tests: {report.iterations} | Gültig: {report.valid} | Abgelehnt: {report.invalid}")
        print(f"Unerwartete Abstürze: {len(report.crashes)}")
        for crash in report.crashes:
            print(f"  {crash.exception_name}: {crash.data!r} -> {crash.path}")
        return 1 if report.crashes else 0

    if args.command == "test":
        if args.message is not None:
            compare_parsers(args.message.encode("utf-8"))
            return 0
        print("Interaktiver Testmodus – Nachrichten selbst eingeben.")
        print("Beispiel: MSG|alice|Hallo | Zum Beenden: exit")
        while True:
            try:
                message = input("Nachricht> ")
            except (EOFError, KeyboardInterrupt):
                print("\nTestmodus beendet.")
                break
            if message.strip().lower() == "exit":
                print("Testmodus beendet.")
                break
            compare_parsers(message.encode("utf-8"))
        return 0

    try:
        data = args.path.read_bytes()
    except OSError as exc:
        print(f"Datei konnte nicht gelesen werden: {exc}", file=sys.stderr)
        return 2
    print(f"Eingabe aus {args.path}: {data!r}")
    compare_parsers(data)
    return 0


def compare_parsers(data: bytes) -> None:
    """Testet die vom Nutzer gewählte Eingabe gegen beide Varianten."""
    print(f"Eingabe: {data!r}")
    for name, target in (("buggy", parse_buggy), ("fixed", parse_fixed)):
        try:
            result = target(data)
            print(f"  {name}: OK -> {result}")
        except InvalidMessage as exc:
            print(f"  {name}: kontrolliert abgelehnt -> {exc}")
        except Exception as exc:
            print(f"  {name}: CRASH -> {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
