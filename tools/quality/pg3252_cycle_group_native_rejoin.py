"""Sealed native28 against new3697; exact1643/79 bytes, no VM or recopy.

451/SS355/PT-OPS-3252-001. The compiled negative harness's old host snapshot
is retained as provenance, never relabelled as new3697. Physical member equality
is required even when new packaging timestamps change the outer jar hash.
"""
import hashlib
import inspect
import json
import os
from pyflakes.api import check
from lan_server import run
from pg1446_current_cold_stage import W
import pg3208_expiry_group_native_rejoin as native27
import pg3234_legacy_negative_native_join as negative
from pg3248_cycle_group_full_six import SOURCE, validate

OUT = W / 'pg3252-cycle-group-native-qualified-v1'


def build(full, original_full, capsule_full, capsule_digest, archive_digest, input_digest):
    if full.get('tests') != 3697 or original_full.get('tests') != 3694 or not (full.get('productionSource') == original_full.get('productionSource') == SOURCE):
        raise ValueError('exact actual3697 and original3694 same-a9 required')
    fn = inspect.getsource(native27.build_payload).replace('3694', '3697').replace('PG3204', 'PG3248').replace('PG3208', 'PG3252')
    ns = dict(native27.__dict__); exec(compile(fn, '<new3697 sealed native27 builder>', 'exec'), ns)
    raw = negative.build(ns['build_payload'](full, capsule_full, capsule_digest), archive_digest, input_digest)
    marker = "meta['sourceSnapshot']==full['sourceSnapshot']"
    if raw.count(marker) != 1: raise ValueError('one original compiled-harness provenance boundary required')
    raw = raw.replace(marker, "meta['sourceSnapshot']==ORIGINAL_FULL['sourceSnapshot']")
    marker = "for m in modules:require(meta['files']['jars/schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar']['sha256']==full['jarHashes'][m])"
    if raw.count(marker) != 1: raise ValueError('one original harness jar/provenance boundary required')
    compare = """for m in modules:
 oldjar=B/'source-full-PG3204/src'/('schubert-nk-'+m)/'target'/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar')
 require(meta['files']['jars/'+oldjar.name]['sha256']==sha(oldjar)==ORIGINAL_FULL['jarHashes'][m])
 images=[]
 for path in [oldjar,jars[m]]:
  with zipfile.ZipFile(path)as image:images.append({name:hashlib.sha256(image.read(name)).hexdigest()for name in image.namelist()if not name.endswith('/')})
 require(images[0]==images[1])
"""
    raw = raw.replace(marker, compare.rstrip().replace('\n', '\n '))
    marker = "with native.open('xb')as f:f.write(material['native.exec']);f.flush();os.fsync(f.fileno())"
    if raw.count(marker) != 1: raise ValueError('one previous fixture native extraction boundary required')
    raw = raw.replace(marker, "require(native.is_file()and not native.is_symlink()and native.read_bytes()==material['native.exec'])")
    raw = 'ORIGINAL_FULL=' + repr(original_full) + '\n' + raw
    if check(raw, '<all same-member28 new3697 qualifier>'): raise ValueError('complete post-build qualifier namespace required')
    compile(raw, '<native28 same Main/resource debug bytes>', 'exec')
    return raw


def main():
    os.umask(0o077)
    current = json.loads((W / 'pg3250-cycle-group-full-qualified-v1/manifest.safe.json').read_bytes())
    original = json.loads((W / 'pg3206-expiry-group-full-qualified-v1/manifest.safe.json').read_bytes())
    capsule_full = json.loads((W / 'pg3056-boundary-group-full-qualified-v1/manifest.safe.json').read_bytes())
    capsule = json.loads((W / 'pg3188-browser-native-qualified-v1/manifest.safe.json').read_bytes())
    post = json.loads((W / 'pg3238-legacy-negative-post-v1/manifest.safe.json').read_bytes())
    compiled = json.loads((W / 'pg3214-legacy-fixture-compile-v1/manifest.safe.json').read_bytes())
    if any(v['actualExit'] != 0 for v in [current, original, capsule_full, capsule, post, compiled]): raise ValueError('every immutable actual input receipt required')
    validate(current['result']['sourceSnapshot'])
    raw = build(current['result'], original['result'], capsule_full['result'], capsule['manifestSha256'], post['capsuleSha256'], compiled['inputSha256'])
    OUT.mkdir(mode=0o700); (OUT / 'payload.private.py').write_text(raw)
    code, output = run("python3 -B - <<'CURRENT'\n" + raw + '\nCURRENT', timeout=240)
    (OUT / 'observer.private.log').write_text(output)
    value = {'actualExit': code, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if code == 0: value.update(json.loads(next(line for line in output.splitlines() if line.startswith('{'))))
    (OUT / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    safe = {'actualExit': code, 'formalAccepted': False}
    if code == 0: safe.update(tests=3697, streams=28, mainClassesSameBytes=1643, resourceMetaSameBytes=79, classByteMismatch=0, remaining={k: sum(v[k]['missed'] for v in value['result']['moduleCounters'].values()) for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']}, manifestSha256=value['manifestSha256'])
    print(json.dumps(safe)); return code


if __name__ == '__main__':
    raise SystemExit(main())
