"""Necessary4197/646/1669 regression for one Web state-result Main, all oracles unchanged."""
import inspect
import json
import subprocess
import pg6768_transfer_io_whole as prior
import pg6780_web_management_result_selected as selected

ROOT,W,BASE,sha=prior.ROOT,prior.W,prior.BASE,prior.sha
LABEL='PG6784'
SLOT='pg6784-web-management-result-six-v1'
QSHA='60eb1d48db665286a8cfd5d4495c51b80e1ee6cce7af282595a96f5f07f99539'


def original_source():
    source=json.loads((W/selected.SLOT/'begin.safe.json').read_bytes())['source'];selected.guard(source);return source


def declared_inventory():return prior.declared_inventory()


def server_source(head,digest):
    return prior.server_source(head,digest).replace('PG6768',LABEL).replace('pg6768','pg6784')


def driver_source(fresh):
    raw=prior.driver_source(fresh).replace(prior.SLOT,SLOT).replace('PG6768',LABEL).replace('pg6768','pg6784')
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Necessary PG-D504 Web management typed stop-result sharing after independent old28/10 '
      'and exact old-state/exception-region source proof. One Main only, every prior Test/quality '
      'gate fixed; full4197/646/1669 fresh XML, no added tests or old PASS arithmetic. Allsix '
      'format-beforePT/compile-null/Werror/static, finite owned tempDB/JMS/HTTP/children only. '
      'No actualRoot/VM/failedcohort/original/Backup/intent/permit/key/native operation. '
      'Original6786 and current SQL/static/JVM/trace required; global/F03/formal separate.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def require_four_counters(c):
    for kind in ('LINE','METHOD','CLASS','BRANCH'):
        value=c.get(kind)
        if not isinstance(value,dict)or type(value.get('missed'))is not int or value['missed']!=0 or type(value.get('covered'))is not int or value['covered']<=0:
            raise ValueError('all original Web four counters explicitly positive and closed')


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('all selected Main/Test/gates fixed')
    qp=BASE/'PG6782-web-management-result-original-v1/manifest.json';pp=W/'pg6782-web-management-result-original-v1/manifest.safe.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze genuine current28/10 original first')
    q,p=[json.loads(x.read_bytes())for x in(qp,pp)]
    if not(q['source']==source and q['actualExit']==0 and(q['tests'],q['suites'],q['physicalMain'])==(28,10,1669)
      and sha(pp)==q['privateManifestSha256']):raise ValueError('genuine original28 all8511669')
    if {x.relative_to(ROOT).as_posix():sha(x)for x in ROOT.glob('src/*/src/main/java/**/*.java')}!=p['allSourceHashes']:raise ValueError('all851 Main exact')
    c=p['allActualCounters']['web:dev/codex/schubert/nk/web/bootstrap/WebManagementServer.class']
    require_four_counters(c)
    from pg6781_web_stop_result_equivalence import verify_source
    verify_source();selected.guard(source);declared_inventory()


def definitions():
    scope={**vars(prior.base),'LABEL':LABEL,'SLOT':SLOT,'original_source':original_source,'prerequisites':prerequisites,
      'server_source':server_source,'driver_source':driver_source}
    raw=inspect.getsource(prior.base.main).replace('pg6188','pg6784')
    exec(compile(raw,'<necessary Web4197 whole>','exec'),scope);return scope


def main():return definitions()['main']()


if __name__=='__main__':raise SystemExit(main())
