"""Fresh PG715 completed21 after current737 ADMIN; preserve all nine private ADMIN trees."""
from pathlib import Path
from pg716_current_baseline import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(),(
        ('pg716-completed-baseline-v1','pg751-completed-baseline-v1'),
        ("base/'pg702-bootstrap-existing-v1/", "base/'pg737-bootstrap-existing-v1/"),
        ('dc4d6a6d35ff09ee28e39068ac95887c879d0babe362929873047464e7f0f562','25e00f13202b08b8db34a8c95b77933ff44cd71d5c37de0fa3cc9aacd5c0609e'),
        ('2464638','2793207'),('12258069','13042489'),
        ('d420de6553ef48038a40332c37a8b12e','0d42d02df3a44b7bb036140f6cc076cf'),
        ('pg696-native-stop-v1','pg728-native-stop-v1'),
        ('6b3dd954959c43c1bbac2164ec9d0c6b','2aff8ecf3b7d4d15b24a8af0f73a8745'),
        ('0.1.0-PG682','0.1.0-PG715'),
        ('076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480','74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ('==524','==534'),("'batchRows':524","'batchRows':534"),
        ("('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1')",
         "('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1','pg737-bootstrap-tools-v1','pg737-bootstrap-verify-v1','pg737-bootstrap-existing-v1')"),
        ("(W/'pg703-bootstrap-final-v4.exit')", "(W/'pg738-bootstrap-final-v1.exit')"),
    ))


if __name__=='__main__':
    env={'__file__':str(R/'pg751_current_baseline.py'),'__name__':'fresh_current21readonly'}
    exec(compile(source(),'<current full21/nine private cohorts read-only>','exec'),env);env['main']()
