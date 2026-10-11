"""New-only after initial unimplemented main compile; old1372 artifacts untouched."""
import pg1372_bootstrap_role_sources as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

def files():
    return {name.replace('1372','1374'):raw.replace('Pg1372','Pg1374').replace('pg1372','pg1374').replace('PG1372','PG1374').replace('pg1374-bootstrap-role-tools-v1','pg1374-bootstrap-role-tools-v2')for name,raw in previous.files().items()}
