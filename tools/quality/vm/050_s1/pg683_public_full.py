"""Redacted PG680 whole-six publication; raw sessions/logs never copied."""
from pathlib import Path

R = Path(__file__).resolve().parent


def source():
    raw = (R/'pg675_public_full.py').read_text()
    for old, new in (
        ('pg672-entry-six-host-v2', 'pg680-owner-six-host-v1'),
        ('PG672-full-public-v1', 'PG680-full-public-v1'),
        ('b66da36efa077a7f41bcfb9777fad702c986dccc07b872962db00495f378a26c', 'b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6'),
        ('(3477, 514, 1608)', '(3489, 516, 1612)'),
        ('549_PG672v2_正規六member回帰再試験.md', '552_PG680_681_所有経路全6回帰仕様.md'),
    ):
        assert old in raw, old
        raw = raw.replace(old, new)
    return raw


if __name__ == '__main__':
    env = {'__file__': str(R/'pg683_public_full.py'), '__name__': 'safe_owner_full_public'}
    exec(compile(source(), '<whitelist whole-six public data>', 'exec'), env)
    env['main']()
