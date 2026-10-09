"""Independent current21 post of actual PG702; no start/stop/restore."""
from pathlib import Path
from pg665_final import source as previous
from pg702_sources import current
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    raw = current(previous()).replace('pg665', 'pg703').replace('PG665', 'PG703')
    raw = replace(raw, (
        ('8767e53ccfc2ea3f434689674dad7395feaef31cec48d53a92bc6fd7eed81c08', '1d70b8f79fb1aa6c1da796b181948334e2a4a7ae962a0365fb5b0c6750c4fb53'),
        ('fa1cd96cc5110f8bb582d7befecb9fd13f66cea63f707b1a03db9e3d5287ef98', 'dc4d6a6d35ff09ee28e39068ac95887c879d0babe362929873047464e7f0f562'),
        ('65bfe1da3b9e454997f1d899fea9510e', 'd420de6553ef48038a40332c37a8b12e'),
        ('111645058422', '122580694582'), ('111646651773', '122582163571'),
        ('111675058422', '122610694582'), ('2142585', '2464638'), ('11164505', '12258069'),
        ('119175', '128965'), ('pg631-manifest.sig', 'pg682-manifest.sig'),
        ('pg703-bootstrap-final-v3', 'pg703-bootstrap-final-v4'),
        ('len(initial)==20', 'len(initial)==21'),
        ("'full20Fields':True", "'full21Fields':True"),
        ("'batchRows':514", "'batchRows':524"), ('1.593351', '1.468989'),
    ))
    # Existing old private proof trees are immutable, not operation output.
    return replace(raw, (("def extra():\n", "def extra():\n for directory,value in initial['currentBootstrapProofs'].items():require(tree(base/directory)==value)\n"),))


if __name__ == '__main__':
    exec(compile(source(), str(R / 'pg703_final.py'), 'exec'),
         {'__name__': '__main__', '__file__': str(R / 'pg703_final.py')})
