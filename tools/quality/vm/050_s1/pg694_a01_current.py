"""Unchanged Current A01 driver on PG690 same source parent, no oracle rewrite."""
from pathlib import Path
from pg654_a01_current import code as previous
from pg692_retention_sources import replace

R=Path(__file__).resolve().parent


def code():
    raw=replace(previous(),(
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5','9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe','076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ('0.1.0-PG631','0.1.0-PG682'),('pg650-fresh-parent-v2','pg690-fresh-parent-v1'),
        ('pg650-start-v2','pg690-start-v1'),('pg651-watch-private-v1','pg691-watch-private-v1'),
        ('pg651-observer-v1','pg691-observer-v1'),('PG654-native-a01-v1','PG694-native-a01-v1'),
        ('pg654-chr-a01-native-v1','pg694-chr-a01-native-v1'),
    ))
    marker="assert (W/'pg690-start-v1.exit').read_bytes()==b'0\\n'"
    assert raw.count(marker)==1
    return raw.replace(marker,marker+"\n    assert (W/'pg692-retention-post-v1.exit').read_bytes()==b'0\\n'")


def main():
    env={'__file__':str(R/'pg694_a01_current.py'),'__name__':'current_a01_new_cohort'}
    exec(compile(code(),'<shared Current driver new cohort>','exec'),env)
    env['main']()


if __name__=='__main__':
    main()
