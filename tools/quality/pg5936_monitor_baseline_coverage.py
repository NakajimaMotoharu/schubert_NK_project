"""Read already-qualified original XML/classes for monitor PG planning; no PT/runtime action."""
import hashlib
import json
import os
import re
import shlex
from lan_server import run
from pg5540_snapshot_scratch_selected import sha
from pg5918_api_static_rebind import SOURCE, W
from static_disposition_overlay import BASE


def reader(data):
    return '''import hashlib,json,pathlib,xml.etree.ElementTree as ET
data='''+repr(data)+'''
base=pathlib.Path('/home/mini/schubert-nk-pgpt');source=base/'source-full-PG5926';terminal=base/'runs/PG5926-six-v1/manifest.safe.json'
if hashlib.sha256(terminal.read_bytes()).hexdigest()!=data['serverManifestSha256']:raise ValueError('exact original genuine terminal')
done=json.loads(terminal.read_bytes())
if done['actualExit']!=0 or done['productionSource']!=data['source']or done['run']!='PG5926-six-v1'or not done['sourceInputsUnchanged']:raise ValueError('original fixed-source whole only')
results=[]
for module in sorted({r['module']for r in data['targets']}):
 path=source/('src/schubert-nk-'+module+'/target/site/jacoco/jacoco.xml');raw=path.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=data['modules'][module]['coverageXmlSha256']:raise ValueError('actual original XML hash')
 classes={c.get('name'):c for c in ET.fromstring(raw).findall('package/class')}
 for target in [r for r in data['targets']if r['module']==module]:
  name=target['class'];key=module+':'+name+'.class';path=source/('src/schubert-nk-'+module+'/target/classes')/(name+'.class')
  if hashlib.sha256(path.read_bytes()).hexdigest()!=data['classes'][key]:raise ValueError('actual current Main class byte identity')
  node=classes.get(name);counts={}if node is None else{c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}for c in node.findall('counter')if c.get('type')in('LINE','METHOD','CLASS','BRANCH')}
  complete=set(counts)=={'LINE','METHOD','CLASS','BRANCH'}and all(c['missed']==0 and(c['covered']>0 or k=='BRANCH')for k,c in counts.items())
  results.append({**target,'classSha256':data['classes'][key],'xmlSha256':data['modules'][module]['coverageXmlSha256'],'counters':counts,'baselineFour100':complete})
print(json.dumps({'actualExit':0,'source':data['source'],'targets':results,'testsReexecuted':0,'vmActions':0}))
'''


def bounded_reader(q, targets):
    if not 1 <= len(targets) <= 64 or len({(r['module'], r['class']) for r in targets}) != len(targets):
        raise ValueError('one bounded unique current artifact target list')
    modules = {r['module'] for r in targets}
    if not modules <= {'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'} or any(
            re.fullmatch(r'dev/codex/schubert/nk/[\w$/]+', r['class']) is None for r in targets):
        raise ValueError('only actual named Main classes in fixed modules')
    keys = {r['module']+':'+r['class']+'.class' for r in targets}
    if not keys <= set(q['allPhysicalMainSha256']) or not modules <= set(q['modules']):
        raise ValueError('all actual class/XML target hashes required')
    data = dict(source=SOURCE, serverManifestSha256=q['serverManifestSha256'], targets=targets,
                classes={key: q['allPhysicalMainSha256'][key] for key in sorted(keys)},
                modules={m: {'coverageXmlSha256': q['modules'][m]['coverageXmlSha256']} for m in sorted(modules)})
    if any(re.fullmatch('[0-9a-f]{64}', v) is None for v in [data['serverManifestSha256'], *data['classes'].values(), *(v['coverageXmlSha256'] for v in data['modules'].values())]):
        raise ValueError('actual original SHA256 only')
    raw = reader(data)
    if len(raw.encode()) > 32768:
        raise ValueError('bounded inline metadata before SSH; no automatic alternate path')
    return raw


def main():
    qp = BASE/'PG5926-current3973-cases/qualification.json'
    if sha(qp) != '89bdeed7bf69067bb0a20c766c8e59cbb780d0fd83dffa7e71c9e1255b1115cf':
        raise ValueError('independent qualified original3973/XML/class proof')
    q = json.loads(qp.read_bytes()); mp = W/'pg5932-private-monitor-facts-v2/manifest.safe.json'
    if sha(mp) != 'c6256fdc92e73e0017ab5603f1572c63174218d6440ba459054b31f42224ca6e':
        raise ValueError('actual typed private monitor/parent-context facts')
    facts = json.loads(mp.read_bytes())
    if facts['source'] != SOURCE or q['productionSource'] != SOURCE or facts['actualExit'] != q['projectionActualExit'] or facts['actualExit'] != 0 or facts['identity']['physicalMainSha256'] != q['allPhysicalMainSha256']:
        raise ValueError('actual current Main type/XML correspondence')
    targets = set()
    for row in facts['facts']['fields']:
        if row['eligible']:
            targets.add((row['path'].split('/')[1].removeprefix('schubert-nk-'), row['owner'].replace('.', '/')))
    for row in facts['facts']['blocks']:
        targets.add((row['path'].split('/')[1].removeprefix('schubert-nk-'), row['blockOwner'].replace('.', '/')))
    raw = bounded_reader(q, [{'module': m, 'class': c} for m, c in sorted(targets)])
    compile(raw, '<original monitor baseline artifact reader>', 'exec')
    os.umask(0o077); private = W/'pg5936-monitor-baseline-v2'; private.mkdir()
    with (private/'reader.private.py').open('x') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    code, text = run('python3 -B -c '+shlex.quote(raw), timeout=90)
    with (private/'observer.private.log').open('x') as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    if code:
        raise ValueError('original artifact read failed; no test or alternate execution')
    result = json.loads(next(s for s in reversed(text.splitlines()) if s.startswith('{')))
    if result['source'] != SOURCE or result['actualExit'] != 0 or len(result['targets']) != len(targets):
        raise ValueError('all original target counter facts')
    out = BASE/'PG5936-private-monitor-baseline-v2'; out.mkdir()
    value = {**result, 'currentWholeQualificationSha256': sha(qp), 'currentTypeFactsSha256': sha(mp),
             'readerSha256': hashlib.sha256(raw.encode()).hexdigest(), 'readerPayloadBytes': len(raw.encode()),
             'maximumInlinePayloadBytes': 32768, 'qualifiedTargets': sum(r['baselineFour100'] for r in result['targets']),
             'baselineOnlyNotNewPgAcceptance': True, 'F03Accepted': False, 'formalAccepted': False, 'ptAlternativeCompleted': 0}
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=SOURCE, targets=len(targets), baselineFour100=value['qualifiedTargets'],
                         incomplete=[{'module': r['module'], 'class': r['class'], 'counters': r['counters']} for r in result['targets'] if not r['baselineFour100']],
                         manifestSha256=sha(out/'manifest.json'), newPgAccepted=False)))


if __name__ == '__main__':
    main()
