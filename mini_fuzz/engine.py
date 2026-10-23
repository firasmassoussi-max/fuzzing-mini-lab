"""Ein kleiner mutationsbasierter Fuzzer mit Crash-Minimierung."""

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .protocol import InvalidMessage, Message

Parser = Callable[[bytes], Message]
SEED_CORPUS = (
    b"MSG|alice|Hallo",
    b"MSG|bob|Test",
    b"MSG|a|x",
)


@dataclass(frozen=True)
class Crash:
    exception_name: str
    data: bytes
    path: Path


@dataclass(frozen=True)
class Report:
    iterations: int
    valid: int
    invalid: int
    crashes: tuple[Crash, ...]


def mutate(raw: bytes, rng: random.Random) -> bytes:
    """Erzeugt eine Variante: Byte ändern, löschen, einfügen oder verkürzen."""
    data = bytearray(raw)
    operation = rng.choice(("flip", "delete", "insert", "replace", "truncate", "duplicate"))

    if operation == "flip" and data:
        index = rng.randrange(len(data))
        data[index] ^= 1 << rng.randrange(8)
    elif operation == "delete" and data:
        del data[rng.randrange(len(data))]
    elif operation == "insert":
        data.insert(rng.randrange(len(data) + 1), rng.randrange(256))
    elif operation == "replace" and data:
        data[rng.randrange(len(data))] = rng.randrange(256)
    elif operation == "truncate":
        del data[rng.randrange(len(data) + 1):]
    elif operation == "duplicate" and data:
        index = rng.randrange(len(data))
        data[index:index] = data[index:index + rng.randint(1, 3)]
    return bytes(data)


def causes_exception(raw: bytes, parser: Parser, expected_name: str) -> bool:
    try:
        parser(raw)
    except InvalidMessage:
        return False
    except Exception as exc:
        return type(exc).__name__ == expected_name
    return False


def minimize(raw: bytes, parser: Parser, expected_name: str) -> bytes:
    """Einfaches Delta Debugging: unnötige Bytes aus einem Crash entfernen.

    Nur wenn derselbe Exception-Typ weiterhin auftritt, bleibt die Änderung.
    """
    current = raw
    granularity = 2
    while len(current) >= 2:
        chunk_size = (len(current) + granularity - 1) // granularity
        smaller = False
        for start in range(0, len(current), chunk_size):
            candidate = current[:start] + current[start + chunk_size:]
            if causes_exception(candidate, parser, expected_name):
                current = candidate
                granularity = max(2, granularity - 1)
                smaller = True
                break
        if smaller:
            continue
        if granularity >= len(current):
            break
        granularity = min(len(current), granularity * 2)
    return current


def run_fuzzer(
    parser: Parser,
    *,
    iterations: int = 2000,
    seed: int = 42,
    out_dir: Path = Path("crashes"),
    max_crashes: int = 3,
) -> Report:
    if iterations < 1:
        raise ValueError("iterations muss mindestens 1 sein")
    if max_crashes < 1:
        raise ValueError("max_crashes muss mindestens 1 sein")

    rng = random.Random(seed)
    valid = 0
    invalid = 0
    crashes: list[Crash] = []
    known_crashes: set[tuple[str, bytes]] = set()
    executed = 0

    for _ in range(iterations):
        executed += 1
        data = mutate(rng.choice(SEED_CORPUS), rng)
        try:
            parser(data)
        except InvalidMessage:
            invalid += 1  # Erwünschte Ablehnung fehlerhafter Eingaben.
        except Exception as exc:
            exception_name = type(exc).__name__
            minimal = minimize(data, parser, exception_name)
            key = (exception_name, minimal)
            if key in known_crashes:
                continue
            known_crashes.add(key)
            out_dir.mkdir(parents=True, exist_ok=True)
            path = out_dir / f"crash_{exception_name}_{len(crashes) + 1:03d}.bin"
            path.write_bytes(minimal)
            crashes.append(Crash(exception_name, minimal, path))
            if len(crashes) >= max_crashes:
                break
        else:
            valid += 1

    return Report(executed, valid, invalid, tuple(crashes))
