"""BOOT702002 independent literal actual new parent/DONE vectors; no VM action."""
from pathlib import Path

R = Path(__file__).resolve().parent
if __name__ == '__main__':
    raw = (R / 'pg662_receipt_test.py').read_text()
    for old, new in (
        ('pg662', 'pg702'), ('BOOT662', 'BOOT702'),
        ('095f6d1d7f8442b7b2b44ae59a4314f5', '6b3dd954959c43c1bbac2164ec9d0c6b'),
        ('109694780700', '121040711116'), ('2026-10-08T22:03:11+00:00', '2026-10-09T01:12:18+00:00'),
        ('111752', '122726'), ('601297d0-a8ba-47da-852b-0ffeae409965', '8633b77f-77dc-4a78-88b4-41165f159b43'),
        ('2026-10-08T21:33:23.332578Z', '2026-10-09T00:43:10.150245Z'),
        ('ad15ac4a-8d8e-4970-bcb3-2e000050ce77', 'c6815985-26c5-4f5f-aed0-abc81fa8f71e'),
        ('2026-10-08T22:03:10.738020Z', '2026-10-09T01:12:17.452418Z'),
        ('1793.235293', '1752.251786'), ('109701545408', '121088459331'),
        ("b'601297d0',b'old297d0'", "b'8633b77f',b'old3b77f'"),
    ):
        assert old in raw, old
        raw = raw.replace(old, new)
    exec(compile(raw, str(R / 'pg702_receipt_test.py'), 'exec'), globals())
