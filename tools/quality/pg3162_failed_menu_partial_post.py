"""Read-only all24 capture and one-Login prefix qualification; no replay/stop."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg3140_browser_business_actual import guard, owned_socks
from pg3160_partial_login_rows_oracle import qualify, TABLES

SLOT = 'pg3162-failed-menu-partial-login-post-v1'


def main():
    os.umask(0o077)
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean partial oracle operator required')
    failed = W / 'pg3140-browser-business-actual-v1'
    manifest = json.loads((failed / 'manifest.safe.json').read_bytes())
    if manifest['actualExit'] != 1 or not manifest['sourceQualified'] or manifest['passedCases'] != 1:
        raise ValueError('exact retained failed Menu cohort required')
    before_raw = (failed / 'cases/before-rows.private.json').read_bytes()
    before = json.loads(before_raw)
    account = json.loads((P / 'pg468-active-account.private.json').read_bytes())
    owners = [row['id'] for row in before['schubert.app_users'] if row['username'] == account['username']]
    if len(owners) != 1:
        raise ValueError('exact already-qualified account required')
    seal = json.loads((W / 'pg3134-browser-resume-full-seal-v1/manifest.safe.json').read_bytes())
    terminal = json.loads((W / 'pg3130-browser-resume-terminal-v1/manifest.safe.json').read_bytes())
    live = json.loads((W / 'pg3124-browser-resume-live-binding-v1/manifest.safe.json').read_bytes())
    raw_guard = guard(seal, terminal, live['binding'])
    sql = "begin isolation level repeatable read read only;set local timezone='UTC';set local statement_timeout='5s';set local lock_timeout='500ms';"
    for table in sorted(before):
        if table not in TABLES:
            raise ValueError('fixed all24 table required')
        sql += "select json_build_object('table','" + table + "','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t) j from " + table + ' t) q;'
    sql += 'commit;'
    out = W / SLOT; out.mkdir(mode=0o700)
    operator = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    socks = owned_socks()
    with management_gate(P / 'current-management-critical.lock'):
        a = subprocess.check_output(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw_guard.encode(), timeout=25)
        result = subprocess.run(SSH + ['sudo', '-n', '-u', 'postgres', 'psql', '-X', '-qAt', '-v', 'ON_ERROR_STOP=1', '-d', 'schubert_nk'], input=sql.encode(), capture_output=True, timeout=30)
        b = subprocess.check_output(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw_guard.encode(), timeout=25)
    if result.returncode or json.loads(a) != json.loads(b) or socks != owned_socks() or len(result.stdout) > 67108864:
        raise ValueError('partial readonly consistent same-owner capture required')
    after = {}
    for line in result.stdout.splitlines():
        value = json.loads(line)
        if value['table'] in after:
            raise ValueError('duplicate table refused')
        after[value['table']] = value['rows']
    context = {'owner': owners[0], 'lower': manifest['startedUTC'], 'upper': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for name, value in [('before', before), ('after', after), ('context', context)]:
        with (out / (name + '.private.json')).open('x') as file:
            json.dump(value, file, sort_keys=True); file.flush(); os.fsync(file.fileno())
    qualified = qualify(before, after, context['owner'], context['lower'], context['upper'])
    value = {'actualExit': 0, 'operatorSource': operator, 'productionSource': manifest['productionSource'], 'sourceQualified': operator == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() and not subprocess.check_output(['git', 'status', '--porcelain']), 'sameFourOwners': True, 'sameSocks': True, 'beforeSha256': hashlib.sha256(before_raw).hexdigest(), 'privateHashes': {name: hashlib.sha256((out / (name + '.private.json')).read_bytes()).hexdigest() for name in ['before', 'after', 'context']}, 'completedUTC': context['upper'], 'result': qualified, 'formalAccepted': False}
    with (out / 'manifest.safe.json').open('x') as file:
        json.dump(value, file, sort_keys=True); file.flush(); os.fsync(file.fileno())
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
