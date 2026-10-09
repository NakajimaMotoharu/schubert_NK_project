"""Current758 ownedstop whole21 snapshot before closingADMIN; allnine oldprivate retained."""
import json
from pathlib import Path
import re
from pg736_current_baseline import source as previous
from pg761_current_binding import bind
from pg662_sources import replace

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def source(post):
    assert type(post)is dict and type(post.get('actualExit'))is int and post['actualExit']==0
    for field in ('all24UnchangedTwice','allTenUnitsKernelEmpty','allActorGone','allClientAdvisoryFlock0','whole187SignedArtifactBytesVerified'):
        assert post[field]is True
    sha=post['proofHashes']['after.private.json']['sha256'];assert type(sha)is str and re.fullmatch('[0-9a-f]{64}',sha)
    raw=bind(previous())
    return replace(raw,(('pg736-completed-baseline-v1','pg767-completed-baseline-v1'),
        ('3dc7e756a77c066f53c7503f8109564c559475ffda98e157c1eb2b0ee62e5c32',sha),
        ('==534','==544'),("'batchRows':534","'batchRows':544"),
        ("('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1')",
         "('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1','pg737-bootstrap-tools-v1','pg737-bootstrap-verify-v1','pg737-bootstrap-existing-v1')")))


if __name__=='__main__':
    post=json.loads((W/'pg765-terminal-final-v1.safe.json').read_bytes())
    exec(compile(source(post),'<current758 whole21readonly>','exec'),{'__file__':str(R/'pg767_current_baseline.py'),'__name__':'__main__'})
