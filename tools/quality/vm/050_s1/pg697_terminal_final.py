"""Independent new current owned-stop full post, no stop reissue."""
from pathlib import Path
from pg692_retention_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace((R/'pg643_terminal_final.py').read_text(),(
        ('pg642','pg696'),('Pg642','Pg696'),('pg640','pg693'),
        ('pg643-terminal-final-v2','pg697-terminal-final-v1'),('PG643-terminal-final-v2','PG697-terminal-final-v1'),
        ("'pg600-manifest.sig', 'pg631-manifest.sig'", "'pg600-manifest.sig', 'pg682-manifest.sig'"),
    ))


if __name__=='__main__':
    exec(compile(source(),'<new source independent stop post>','exec'),
         {'__file__':str(R/'pg697_terminal_final.py'),'__name__':'__main__'})
