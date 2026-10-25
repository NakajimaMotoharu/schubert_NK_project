"""Fixed public G07 input metadata only; no scanner, Git history blob replay or target reads."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
TRACKED=ROOT.parent/'pgpt-runs/PG379/pg8968-public-blob-scan-v1/tracked'
NORMAL=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1/snapshot'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
CONTENT='05d73a7974da8df92228160b96d91e7a006768f3'
HISTORICAL='fb9fce0f91de3d9fdfa634fe277592700f915e45'
PINS={
 'scan':('PG8968-public-blob-scan-v1','f8e16b697c1c509791c6674bb17661c54e8685c0f04425bed8bf7ea86a94a739'),
 'prior':('PG8980-public-finding-provenance-v1','fe4175077735018f5b500306e09c7300917a814c53196a2378e1b1e887b6f5ae'),
 'ancestor':('PG8990-public-ancestor-provenance-v1','23ce1b56dffe743048e2c5fd07fc09c94e026c947c2711487420dcfdb8732be6'),
 'tokens':('PG9000-public-token-provenance-v1','c3216ab47b1ebe8a9da9c6587b1784b99b89a46390e1f0c61c80154dcc9f1847'),
 'tokenPost':('PG9002-public-token-provenance-post-v1','3af5c448f053d77bac336122f4f7372e7bffa41aacea24052456f07c06f7a177'),
 'normal':('PG9246-web-life-lock-six-compile-v1','989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'),
 'graph':('PG9386-composite-reference-graph-v3','3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15')}

def sha(data):return hashlib.sha256(data).hexdigest()
def read_checked(path,digest):
    raw=path.read_bytes()
    if sha(raw)!=digest:raise ValueError('immutable public metadata digest required')
    return json.loads(raw)
def key(row):return tuple(row[k] for k in ('path','ruleId','startLine','endLine','inputSha256'))
def inputs():
    manifests={k:read_checked(BASE/name/'manifest.json',digest) for k,(name,digest) in PINS.items()}
    assert all(v['actualExit']==0 for v in manifests.values())
    assert manifests['scan']['source']==manifests['prior']['source']==manifests['ancestor']['source']==manifests['tokens']['source']==HISTORICAL
    assert manifests['scan']['contentCommit']==manifests['tokens']['contentCommit']==CONTENT
    assert manifests['tokens']['remainingUnclassified']==8379 and manifests['tokens']['cumulativeFalsePositiveProof']==31707
    assert manifests['tokenPost']['remainingUnclassified']==8379 and manifests['tokenPost']['additionalFalsePositives']==1581
    assert manifests['normal']['source']==manifests['graph']['source']==SOURCE
    prior=read_checked(BASE/PINS['prior'][0]/'classifications.json',manifests['prior']['classificationSha256'])
    inventory=read_checked(BASE/PINS['scan'][0]/'inventory.json',manifests['scan']['inventorySha256'])['rows']
    original=read_checked(BASE/PINS['scan'][0]/'findings.json',manifests['scan']['findingsSha256'])
    assert len(original)==len(prior)==40086 and Counter(map(key,original))==Counter(map(key,prior))
    proofs={}
    for row in inventory:
        proofs.setdefault(row['sha256'],dict(proofKind='CURRENT_PUBLIC_BLOB',path=row['path'],sha256=row['sha256'],gitObject=row['gitObject']))
    ancestor=read_checked(BASE/PINS['ancestor'][0]/'public-proofs.json',manifests['ancestor']['proofsSha256'])
    for p in ancestor:proofs.setdefault(p['sha256'],p)
    done=Counter()
    for label in ('ancestor','tokens'):
        updates=read_checked(BASE/PINS[label][0]/'updates.json',manifests[label]['updatesSha256'])
        done.update(map(key,updates))
        if label=='tokens':
            for row in updates:
                for p in row['publicArtifactProofs']:
                    name='publicTokenDigest' if p.get('proofKind')=='PUBLIC_JAVA_SQLCATCH_TOKEN_DIGEST' else 'sha256'
                    assert name in p;proofs.setdefault(p[name],p)
    pending=[]
    for row in prior:
        if row['disposition']!='UNCLASSIFIED':continue
        identity=key(row)
        if done[identity]:done[identity]-=1
        else:pending.append(row)
    assert len(pending)==8379 and sum(done.values())==0
    main_map=read_checked(BASE/PINS['graph'][0]/'main-class-sources.json',manifests['graph']['mainMapSha256'])
    config_raw=(BASE/'PG8979-gitleaks-rule-provenance-v1/manifest.json').read_bytes()
    assert sha(config_raw)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a'
    config=json.loads(config_raw)
    assert config['configSha256']=='e163e53b9e7e8a8511e77271e2b323ed057759542a6d988258afe3a1fa329caf'
    return dict(manifests=manifests,pending=pending,oldProofs=proofs,inventory={r['path']:r for r in inventory},
      mainMap=main_map,rules=config['rules'],ruleProvenanceSha256=sha(config_raw))

def finding_text(row,inventory):
    relative=Path(row['path'])
    assert not relative.is_absolute() and '..' not in relative.parts
    path=TRACKED/relative
    assert path.resolve()==path and path.is_relative_to(TRACKED) and inventory[row['path']]['sha256']==row['inputSha256']
    raw=path.read_bytes();assert sha(raw)==row['inputSha256']
    return raw.decode('utf-8')

def regular_normal_jar(module,entry):
    path=Path(entry['path'])
    assert path.resolve()==path and not path.is_symlink() and path.suffix=='.jar'
    assert path.is_relative_to(NORMAL/('src/schubert-nk-'+module)/'target')
    assert sha(path.read_bytes())==entry['sha256']
    return path

def write(path,value):
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
