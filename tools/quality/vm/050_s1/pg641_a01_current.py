"""Unchanged Current A01 driver, new same-parent source/slots; no restart/baseline edit."""
import ast
from pathlib import Path


def code():
    value = (Path(__file__).parent/'pg607_a01_when_ready.py').read_text()
    for old, new in (
        ('23b14a44b10504172e030bbd6625926bf049fb5c', '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'),
        ('a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f', '57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'),
        ('0.1.0-PG600', '0.1.0-PG631'), ('pg605-fresh-parent-v2', 'pg637-fresh-resume-v2'),
        ('pg605-start-v2', 'pg637-start-v2'), ('pg606-watch-private-v1', 'pg638-watch-private-v1'),
        ('pg606-observer-v1', 'pg638-observer-v1'), ('PG607-native-a01-v1', 'PG641-native-a01-v1'),
        ('pg607-chr-a01-native-v1', 'pg641-chr-a01-native-v1'),
    ):
        assert old in value
        value = value.replace(old, new)
    return value


def main():
    env = {'__name__': 'current_a01_capture', '__file__': str(Path(__file__).resolve())}
    exec(compile(code(), '<same Current driver, fixed new source>', 'exec'), env)
    env['main']()


def guard():
    tree = ast.parse(code())
    node = next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'GUARD' for t in n.targets))
    return ast.literal_eval(node.value)


if __name__ == '__main__': main()
