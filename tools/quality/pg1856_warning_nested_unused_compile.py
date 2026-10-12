"""BUG1181: canonical nested write/inventory with all immutable graph gates retained."""
import inspect
import json
import pg1850_warning_signed_unused_compile as prior
from pg1645_completed_candidate_compile_v2 import canonical_relative,inventory
from pg1855_warning_nested_unused_sources import sources,TOOLS,bind

TARGET=prior.engine.W/TOOLS
ARCHIVE=prior.engine.P/'pg1857-warning-release-v1.tar'


def write(path,raw):
    if path.is_relative_to(TARGET):
        canonical_relative(str(path.relative_to(TARGET)))
        path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    prior.engine.write(path,raw)


def validate_actual_graph(target,hashes):
    raw=bind(inspect.getsource(prior.validate_actual_graph))
    ns={**prior.__dict__,'ARCHIVE':ARCHIVE};exec(compile(raw,'<actual nested graph function>','exec'),ns)
    return ns['validate_actual_graph'](target,hashes)


def compiler():
    raw=bind(prior.compiler()).replace('pg1850-','pg1856-')
    marker="    hashes = {p.name: sha(p) for p in TARGET.iterdir() if p.is_file()}"
    if raw.count(marker)!=1:raise ValueError('one flat inventory boundary required')
    raw=raw.replace(marker,'    hashes = inventory(TARGET)')
    raw=raw.replace('for p in TARGET.iterdir():','for p in TARGET.rglob("*"):\n        if not p.is_file():continue')
    compile(raw,'<actual all nested immutable helpers compile>','exec');return raw


def main():
    before=json.loads((prior.engine.W/'pg1849-warning-completed-current-before-v1/manifest.safe.json').read_bytes())
    if before['actualExit']!=0 or before['productionSource']!=prior.OLD or before['genuineCompletion']['managerFailureRetained']is not True:raise ValueError('same actual current closed warning required')
    digest=before['privateBeforeSha256']
    ns={**prior.engine.__dict__,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'TOOLS':TOOLS,'CURRENT':prior.OLD,'PRODUCTION':prior.CANDIDATE,'BEFORE':digest,'sources':lambda bom:sources(bom,digest),'validate_actual_graph':validate_actual_graph,'write':write,'inventory':inventory}
    exec(compile(compiler(),'<new-only nested complete freeze>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
