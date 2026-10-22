"""Own static Caddyfile adaptation only; explicitly no provision, keys, TLS or daemon."""
import datetime
import hashlib
import json
import os
import subprocess
import tarfile
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6932_original4222_artifacts import read_whole
from pg6092_current3985_static_join import source_case_candidates

BIN = ROOT.parent.parent / 'work/characterization-tools/root/usr/bin/caddy'
BIN_SHA = '678c1849799e6d81c7cfbe63cebb8f92400cb70a67fc9f601697cb8ce7cdfa4a'
ARTIFACT = 'src/deployment/caddy/Caddyfile.template'
DESIGN = 'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CaddyPublicConfigurationTest.java'
SLOT = 'pg6948-c01-static-adapt-v1'


def normal(text):
    return '\n'.join(s.strip() for s in text.splitlines() if s.strip() and not s.lstrip().startswith('#'))


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def verify_json(value, address):
    nodes = list(walk(value))
    servers = list(value['apps']['http']['servers'].values())
    listen = address if ':' not in address else '[' + address + ']'
    if len(servers) != 1 or servers[0]['listen'] != [listen + ':55160'] or value['admin'] != {'disabled': True}:
        raise ValueError('one exact IP55160 listener declaration and disabled admin, not observed listening')
    if not servers[0]['automatic_https']['disable_redirects'] or value['apps']['pki']['cas']['local']['install_trust'] is not False:
        raise ValueError('no redirect listener or trust-store installation declaration')
    handlers = [n for n in nodes if 'handler' in n]
    if {n['handler'] for n in handlers} != {'subroute', 'request_body', 'headers', 'reverse_proxy'}:
        raise ValueError('only the fixed four handler kinds, no direct file/media service')
    body = [n for n in handlers if n['handler'] == 'request_body']
    # SS says 2MB; vendor ParseBytes uses SI MB, independently 2 * 1000 * 1000.
    if len(body) != 1 or body[0]['max_size'] != 2000000:
        raise ValueError('exact SS2MB decimal bytes, never silently substitute 2MiB')
    proxy = [n for n in handlers if n['handler'] == 'reverse_proxy']
    if len(proxy) != 1 or proxy[0]['upstreams'] != [{'dial': '127.0.0.1:8080'}]:
        raise ValueError('one loopback Web upstream only')
    transport = proxy[0]['transport']
    if any(transport.get(k) != v for k, v in dict(protocol='http', dial_timeout=2000000000,
      response_header_timeout=30000000000, read_timeout=60000000000, write_timeout=60000000000).items()):
        raise ValueError('same SS2/30/60/60 second transport budget')
    expected_up = {'X-Forwarded-For': ['{http.request.remote.host}'],
      'X-Forwarded-Proto': ['{http.request.scheme}'], 'X-Forwarded-Host': ['{http.request.host}']}
    if proxy[0]['headers']['request']['set'] != expected_up or any('trusted_proxies' in n for n in nodes):
        raise ValueError('reconstruct forwarded values, no trusted proxy declaration')
    headers = [n['response'] for n in handlers if n['handler'] == 'headers']
    expected_headers = {'Strict-Transport-Security': ['max-age=31536000'], 'X-Content-Type-Options': ['nosniff'],
      'X-Frame-Options': ['DENY'], 'Referrer-Policy': ['same-origin']}
    if len(headers) != 1 or headers[0]['set'] != expected_headers or headers[0]['delete'] != ['Server']:
        raise ValueError('fixed four response headers, remove Server; Web owns CSP')
    issuers = [n['module'] for n in nodes if 'module' in n]
    if issuers != ['internal']:
        raise ValueError('one internal issuer declaration, no actual CA/key provision')


def main():
    qp, q, cases = read_whole()
    if sha(qp) != '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731' or sha(BIN) != BIN_SHA:
        raise ValueError('frozen original current4222 and pinned existing Caddy2.6.2')
    source = q['productionSource']
    design = subprocess.check_output(['git', 'show', 'origin/main:' + DESIGN], cwd=ROOT)
    if design != (ROOT / DESIGN).read_bytes():
        raise ValueError('canonical design/current tree agree')
    oracle = design.decode().split('```caddyfile\n', 1)[1].split('\n```', 1)[0]
    text = (ROOT / ARTIFACT).read_text()
    if normal(text) != normal(oracle):
        raise ValueError('full independent SS logical profile, no inferred missing directives')
    inventory = json.loads((ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    owned = {a['path']: a['sha256'] for a in inventory['currentPhysicalCandidate']['artifacts'] if a['owner'] == 'WBS-C01'}
    if owned != {ARTIFACT: sha(ROOT / ARTIFACT)}:
        raise ValueError('exact entire C01 owned scope/hash, no unreviewed extra artifact')
    original = W / 'pg6930-fixture4222-six-v1'
    begin = json.loads((original / 'begin.safe.json').read_bytes())
    if begin['source'] != source or sha(original / 'source.tar') != begin['archiveSha256']:
        raise ValueError('source archive fixed')
    with tarfile.open(original / 'source.tar') as tar:
        for path in (ARTIFACT, TEST):
            item = tar.getmember(path)
            if not item.isfile() or tar.extractfile(item).read() != (ROOT / path).read_bytes() or subprocess.check_output(['git', 'show', source + ':' + path], cwd=ROOT) != (ROOT / path).read_bytes():
                raise ValueError('both original config and Test inputs fixed')
    methods = ('caddy455006Ipv4Ipv6AndFormattingRemainTlsOnly', 'caddy455007AnyUnexpectedDirectiveOrAddressFailsClosed',
      'caddy455008DeploymentTemplateMatchesIndependentDirectiveSet')
    joined = []
    for index, name in enumerate(methods, 6):
        digest = hashlib.sha256(source_case_candidates((ROOT / TEST).read_text(), name)[0].encode()).hexdigest()
        found = [c for c in cases if c['class'] == 'dev.codex.schubert.nk.batch.file.CaddyPublicConfigurationTest' and c['caseNameSha256'] == digest]
        if len(found) != 1 or found[0]['result'] != 'PASS_ORIGINAL_XML' or found[0]['source'] != source:
            raise ValueError('one current original case per CADDY455 method')
        joined.append(dict(testId=f'CADDY455{index:03}', method=name, originalCase=found[0]))
    os.umask(0o077)
    slot = W / SLOT
    slot.mkdir()
    env = {'PATH': os.defpath, 'LANG': 'C.UTF-8', 'GOMAXPROCS': '1',
      'XDG_DATA_HOME': str(slot / 'xdg-data'), 'XDG_CONFIG_HOME': str(slot / 'xdg-config'), 'XDG_CACHE_HOME': str(slot / 'xdg-cache')}
    rows = []
    for index, address in enumerate(('127.0.0.1', '2001:db8::1'), 1):
        host = address if ':' not in address else '[' + address + ']'
        rendered = text.replace('https://<GLOBAL_IP>', 'https://' + host).replace('bind <GLOBAL_IP>', 'bind ' + address)
        path = slot / (str(index) + '.Caddyfile')
        with path.open('x') as f:
            f.write(rendered)
        command = [str(BIN), 'adapt', '--config', str(path), '--adapter', 'caddyfile']
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result = subprocess.run(command, cwd=slot, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15, check=False)
        # Only fixed input/private raw output. No daemon, --validate/provision, environment display or TLS key access.
        for suffix, raw in (('json', result.stdout), ('stderr.private.log', result.stderr)):
            with (slot / (str(index) + '.' + suffix)).open('xb') as f:
                f.write(raw)
        if result.returncode != 0:
            raise ValueError('original static adapt failed; preserve slot, do not rerun automatically')
        value = json.loads(result.stdout)
        verify_json(value, address)
        rows.append(dict(testId=f'PT-C01-ADAPT-{index:03}', address=address, actualExit=result.returncode,
          command=command, startedUTC=started, inputSha256=sha(path), outputSha256=sha(slot / (str(index) + '.json')),
          stderrSha256=hashlib.sha256(result.stderr).hexdigest(), stderrPresent=bool(result.stderr),
          sourceConfigSha256=sha(ROOT / ARTIFACT), plainAdaptOnly=True, provisioned=False))
    if any((slot / n).exists() for n in ('xdg-data', 'xdg-config', 'xdg-cache')):
        raise ValueError('unexpected XDG state from static transform; retain private, no success inference')
    value = dict(actualExit=0, source=source, artifact=ARTIFACT, artifactSha256=sha(ROOT / ARTIFACT),
      designMain=subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip(),
      designSha256=hashlib.sha256(design).hexdigest(), originalQualificationSha256=sha(qp), originalCases=joined,
      caddyVersion='2.6.2', caddyBinarySha256=BIN_SHA, staticAdaptCases=rows, originalTestsReplayed=False,
      javaPassCountAdded=0, measuredCoverageAdded=False, newStaticAdaptCases=2,
      qualifiedLocalCriteria=['WBS-C01:contract', 'WBS-C01:scope'],
      unaccepted=['WBS-C01:quality full fmt/adapt--validate/validate and real TLS/active config/runtime gates remain separate',
                   'canonical historical17 not rebased; no new mixed-source acceptance'],
      actualServiceActions=0, vmActions=0, TLSOrKeyOperations=0, acceptedLeafDelta=0, formalAccepted=False,
      effortPercent=None, ptAlternativeCompleted=0, toolSha256=sha(ROOT / 'tools/quality/pg6948_c01_static_adapt.py'))
    out = BASE / 'PG6948-c01-static-adapt-v1'
    out.mkdir()
    for index in (1, 2):
        for suffix in ('Caddyfile', 'json'):
            with (out / (str(index) + '.' + suffix)).open('xb') as f:
                f.write((slot / (str(index) + '.' + suffix)).read_bytes())
    with (out / 'manifest.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(out / 'manifest.json'), originalCases=3, staticAdaptCases=2,
      localCriteria=2, qualityComplete=False, acceptedLeafDelta=0)))


if __name__ == '__main__':
    main()
