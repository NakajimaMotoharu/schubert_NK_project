"""Fixed D5 completed cold runtime; generation only, never VM stop authority.

SS343/353/SSC190/191/260; PT-DEP-1198001..005. The full1197 seal
is mandatory. Old source/native success is not copied into this current run.
"""
import ast
import inspect
from pathlib import Path
import pg963_current_stop_binding as old
import pg1131_journal_stable_projection as journal
import pg1196_completed_rows_oracle as rows_oracle

R = Path(__file__).resolve().parent
SOURCE = 'd5b00104280028d9ea81b44c1d1c805f3c2861ed'
DIGEST = '0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d'
BEFORE = '398324fdea98d2469067a1e93858cd292b4e0328da5712b709c7bb99cffeadfa'
ROOT = '/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/completed-current-before-v1'
OWNED = {'caddy.service': ('528966', '1037150931c04cb6b64b249c0cf916c3'),
         'schubert-nk-web.service': ('526861', '898429f0e6a64d4fa7a6c07e4473fe8a'),
         'schubert-nk-api.service': ('525675', 'bfae0cf915c74f7bbf35a7a1ec4f8cd9'),
         'artemis.service': ('441175', 'c874395201b94ae7b144e3a6bb2d3b8e')}
VALUES = (
    ('Pg963', 'Pg1198'), ('PG963', 'PG1198'), ('pg963', 'pg1198'),
    ('PG932', 'PG1068'), ('pg932', 'pg1068'), (old.SOURCE, SOURCE),
    ('b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524', DIGEST),
    ('eeae04ea-713c-4f2d-888d-358fb4bed274', '343a5a1b-d064-47d5-88c2-31c36d7ba7a4'),
    ('2026-10-09T23:31:22.087768Z', '2026-10-10T12:40:27.396847Z'),
    ('2026-10-09T23:31:22.087768+00:00', '2026-10-10T12:40:27.396847+00:00'),
    ('091663ce-1cf4-47e7-8311-218ebb0c8653', 'ada3f7ff-8287-48d7-9ba9-5cce71f61bd3'),
    ('0bb4d6f3b9e74cdc91c553748a4cd018', 'a14cc600a4fd4f2e9d8c4731ad9d754b'),
    ('201380374989', '51172132518'), ('203180374989', '52972132518'),
    ('213904', '81093'), ('3844442', '430851'),
    ('cc9ed874-7f4f-450e-a188-8de1e42c8441', 'cbca8738-3b24-4090-b77c-bf029677cdd6'),
    ('cc9ed8747f4f450ea1888de1e42c8441', 'cbca87383b244090b77cbf029677cdd6'),
    ('pg960-completed-readonly-v1', ROOT.removeprefix('/var/lib/pgpt-s1-preservation/')),
)


def bind(raw):
    for a, b in VALUES:
        raw = raw.replace(a, b)
    return raw


def namespace():
    raw = bind(old.module_source())
    env = {'__file__': str(R/'pg1198_current_stop_binding.py'), '__name__': 'current_d5_stop_generation'}
    exec(compile(raw, '<fixed current D5 stop generation>', 'exec'), env)
    return env


def bindings(proof):
    if type(proof) is not dict or proof.get('beforeSha256') != BEFORE:
        raise ValueError('qualified actual full current seal required')
    if proof.get('parentEndedUTC') != '2026-10-10T17:37:58.505406Z':
        raise ValueError('actual current DONE UTC required')
    units = proof.get('ownedUnits')
    if type(units) is not dict or set(units) != set(OWNED) or any(
            type(units[u]) is not dict or (units[u].get('MainPID'), units[u].get('InvocationID')) != pair
            for u, pair in OWNED.items()):
        raise ValueError('exact current four ordinary generations required')
    return namespace()['bindings'](proof)


def replace_once(raw, a, b):
    if raw.count(a) != 1:
        raise ValueError('fixed current generated closure insertion refused: '+a[:55])
    return raw.replace(a, b)


def generate(proof):
    bindings(proof)
    values = namespace()['generate'](proof)
    # Historical mapping changes constants outside factory literals as well.
    values = {name: bind(raw) for name, raw in values.items()}
    refs = values['pg1198_native_refs.py']
    refs = replace_once(refs, "j=[json.loads(l)for l in journal.splitlines()];verify_pid1(j)",
                        "j=json.loads(stable_journal.project(journal));verify_pid1(j);JOURNAL_READS.append(journal)")
    refs = replace_once(refs, "UNITS,FIELDS=sealed['UNITS'],sealed['FIELDS']",
                        "UNITS,FIELDS=sealed['UNITS'],sealed['FIELDS']\n import pg1198_stable_journal as stable_journal\n from pg1198_row_bound import output_bound\n JOURNAL_READS=[]")
    marker = "for line in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines():"
    refs = replace_once(refs, marker,
        "rp=subprocess.run(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)\n  output_bound(rp.returncode,len(rp.stdout))\n  for line in rp.stdout.splitlines():")
    refs = replace_once(refs, "return {'units':units,'configuration':cfg,'rows':data,'pid1':j,'startup':tree(startup),'originals':tree(pathlib.Path('/var/lib/schubert-nk/maintenance')),'backup':tree(pathlib.Path('/srv/schubert-nk/backup'))}",
        "durable=json.loads(original)['durable']\n  extra={k:tree(pathlib.Path(min(v,key=len)))for k,v in durable.items()if k not in {'originals','backup'}}\n  files=json.loads(original)['unitFiles'];file_entries={p:metadata(pathlib.Path(p))+[hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()]for p in files}\n  runtime=tree(pathlib.Path('/run/systemd/system'))\n  return {'units':units,'configuration':cfg,'rows':data,'pid1':j,'startup':tree(startup),'originals':tree(pathlib.Path('/var/lib/schubert-nk/maintenance')),'backup':tree(pathlib.Path('/srv/schubert-nk/backup')),'extraDurable':extra,'unitFilesActual':file_entries,'runtime':runtime}")
    refs = replace_once(refs, "save('after.private.json',capture_data(False))",
        "save('after.private.json',capture_data(False))\n   for i,raw_journal in enumerate(JOURNAL_READS):durable_save(SAVE,'parent-journal-read-'+str(i)+'.private.jsonl',raw_journal)")
    refs = replace_once(refs, "h.parent_receipt();captures={u:first['units'][u]for u in h.ORDER}",
        "require(first['runtime']==prior['runtime'] and all(first['extraDurable'][k]==prior['durable'][k]for k in first['extraDurable']))\n for path,value in prior['unitFiles'].items():require(first['unitFilesActual'][path]==value['metadata']+[value['sha256']])\n h.parent_receipt();captures={u:first['units'][u]for u in h.ORDER}")
    values['pg1198_native_refs.py'] = refs
    values['pg1198_stable_journal.py'] = inspect.getsource(journal)
    # Small standalone independent numeric bound, not production result oracle.
    t = ast.parse(inspect.getsource(rows_oracle))
    wanted = [n for n in t.body if (isinstance(n, ast.FunctionDef) and n.name in {'require', 'output_bound'})
              or (isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'LIMIT' for x in n.targets))]
    if len(wanted) != 3:
        raise ValueError('full row numeric bound closure required')
    values['pg1198_row_bound.py'] = ast.unparse(ast.Module(body=wanted, type_ignores=[]))+'\n'
    for name, raw in values.items():
        if name.endswith('.py'):
            ast.parse(raw)
    return values
