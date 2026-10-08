"""Shared Current A01 driver on new ordinary parent; no baseline or unit edit."""
from pathlib import Path
from pg641_a01_current import code as previous


def code():
    raw=previous()
    for old,new in (
        ('pg637-fresh-resume-v2','pg650-fresh-parent-v2'),('pg637-start-v2','pg650-start-v2'),
        ('pg638-watch-private-v1','pg651-watch-private-v1'),('pg638-observer-v1','pg651-observer-v1'),
        ('PG641-native-a01-v1','PG654-native-a01-v1'),('pg641-chr-a01-native-v1','pg654-chr-a01-native-v1'),
    ):
        assert old in raw;raw=raw.replace(old,new)
    return raw


def main():
    env={'__name__':'new_ordinary_current_driver','__file__':str(Path(__file__).resolve())}
    exec(compile(code(),'<unchanged Current driver on new ordinary parent>','exec'),env)
    env['main']()


if __name__=='__main__':main()
