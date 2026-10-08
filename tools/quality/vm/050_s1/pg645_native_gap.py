"""New current-source gap coordinates only, no old cohort/evidence re-import."""
from pathlib import Path


def code():
    value = (Path(__file__).parent/'pg615_current_native_gap.py').read_text()
    for old, new in (
        ('pg614-current-eight-native-v1', 'pg644-current-eight-native-v1'),
        ('4c178d8e6d2f76f097a315226586bb934041ce1805a5cd79811e2034b3b442c1', '3200b4a2e5b5bd63a5854dbb541c22ca66cdb14bc98fde75173797a96bb68aa0'),
        ('23b14a44b10504172e030bbd6625926bf049fb5c', '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'),
        ('pg615-current-native-gap-v1', 'pg645-current-native-gap-v1'),
        ('pg599-candidate-bootstrap-six-host-v1', 'pg630-retention-factory-six-host-v1'),
    ):
        assert old in value
        value = value.replace(old, new)
    return value


if __name__ == '__main__':
    env = {'__name__': 'fixed_current_gap', '__file__': str(Path(__file__).resolve())}
    exec(compile(code(), '<same fixed XML counter, new verified source>', 'exec'), env)
    env['main']()
