"""Zwei Versionen eines kleinen Protokoll-Parsers.

Nachrichtenformat (UTF-8): MSG|absender|nachricht
Beispiel: b"MSG|alice|Hallo"
"""

from dataclasses import dataclass

MAX_PACKET_BYTES = 256


class InvalidMessage(ValueError):
    """Fehlerhaftes Eingabepaket – ein erwarteter Fehler, kein Programmabsturz."""


@dataclass(frozen=True)
class Message:
    sender: str
    body: str


def _decode(raw: bytes) -> str:
    if len(raw) > MAX_PACKET_BYTES:
        raise InvalidMessage("Nachricht zu lang")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidMessage("Ungültige UTF-8-Kodierung") from exc


def parse_buggy(raw: bytes) -> Message:
    """Absichtlich fehlerhafter Parser: prüft die Anzahl der Felder zu spät.

    Ein Paket wie b'MSG|alice' führt zu IndexError. Das ist unser Lern-Bug.
    """
    fields = _decode(raw).split("|", maxsplit=2)
    if fields[0] != "MSG":
        raise InvalidMessage("Unbekannter Nachrichtentyp")

    sender = fields[1]  # BUG: fields[1] existiert eventuell nicht.
    body = fields[2]    # BUG: fields[2] existiert eventuell nicht.

    if not sender or not body:
        raise InvalidMessage("Absender oder Nachricht leer")
    return Message(sender=sender, body=body)


def parse_fixed(raw: bytes) -> Message:
    """Korrigierter Parser: kontrolliert das Format vor dem Zugriff."""
    fields = _decode(raw).split("|", maxsplit=2)
    if len(fields) != 3:
        raise InvalidMessage("Genau drei Felder erforderlich: MSG|absender|nachricht")
    kind, sender, body = fields
    if kind != "MSG":
        raise InvalidMessage("Unbekannter Nachrichtentyp")
    if not sender or not body:
        raise InvalidMessage("Absender oder Nachricht leer")
    return Message(sender=sender, body=body)
