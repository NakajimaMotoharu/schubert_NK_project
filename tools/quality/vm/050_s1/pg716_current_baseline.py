"""Fresh current9bd full21 before candidate deployment; both ADMIN private cohorts retained."""
from pathlib import Path
from pg684_completed_baseline_v2 import source as previous
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    raw = replace(previous(), (
        ('pg684-completed-baseline-v2', 'pg716-completed-baseline-v1'),
        ('pg664-bootstrap-existing-v1', 'pg702-bootstrap-existing-v1'),
        ('pg664-bootstrap-tools-v1', 'pg702-bootstrap-tools-v1'),
        ('pg664-bootstrap-verify-v1', 'pg702-bootstrap-verify-v1'),
        ('fa1cd96cc5110f8bb582d7befecb9fd13f66cea63f707b1a03db9e3d5287ef98', 'dc4d6a6d35ff09ee28e39068ac95887c879d0babe362929873047464e7f0f562'),
        ('2142585', '2464638'), ('11164505', '12258069'),
        ('65bfe1da3b9e454997f1d899fea9510e', 'd420de6553ef48038a40332c37a8b12e'),
        ('pg655-native-stop-v1', 'pg696-native-stop-v1'),
        ('095f6d1d7f8442b7b2b44ae59a4314f5', '6b3dd954959c43c1bbac2164ec9d0c6b'),
        ('0.1.0-PG631', '0.1.0-PG682'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe', '076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5', '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('==514', '==524'), ("'batchRows':514", "'batchRows':524"),
        ("(W/'pg656-terminal-final-v1.exit')", "(W/'pg703-bootstrap-final-v4.exit')"),
        ("('pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1')",
         "('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1')"),
        ('require(len(v)==21);return v', "for key in ('credentials','native','startup','originals','backup','oldProofs','parentPid1','rows','namespace','dependencies'):require(v[key]==old[key])\n  require(len(v)==21);return v"),
    ))
    return raw


if __name__ == '__main__':
    env = {'__file__': str(R / 'pg716_current_baseline.py'), '__name__': 'fresh_current_readonly'}
    exec(compile(source(), '<completed21 including both private ADMIN cohorts>', 'exec'), env)
    env['main']()
