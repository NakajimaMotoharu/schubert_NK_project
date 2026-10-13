"""Changed Main selection: real strict parser vectors and data-only current-run lookup."""
import inspect
import pg2112_caddy_metadata_selected as transport
from pg2116_caddy_metadata_selected_v3 import server as dependency_server
from pyflakes.api import check

TARGETS = {
    'dev/codex/schubert/nk/batch/platform/BrokerJournalEvidence#fields': True,
    'dev/codex/schubert/nk/batch/repository/MorningDatabaseSession#currentRunReference': False,
    'dev/codex/schubert/nk/batch/repository/MorningDatabaseSession#lambda$currentRunReference$0': True}


def validate_method_scope(scopes):
    if type(scopes) is not dict or set(scopes) != set(TARGETS):
        raise ValueError('exact three changed method scopes required')
    for name, has_branch in TARGETS.items():
        counters = scopes[name]
        for key in ['LINE', 'METHOD'] + (['BRANCH'] if has_branch else []):
            value = counters.get(key, {})
            if type(value.get('missed')) is not int or value['missed'] != 0 or type(value.get('covered')) is not int or value['covered'] <= 0:
                raise ValueError('changed method actual counter incomplete')
        if not has_branch and 'BRANCH' in counters:
            raise ValueError('factory declared without conditions must not hide new branches')


def server():
    raw = dependency_server().replace('PG2116', 'PG2504')
    raw = raw.replace('-Dtest=CaddyPublicMetadataTest,CaddyPublicConfigurationTest,CaddyPublicCaMetadataTest,CaddyAddressBoundaryTest', '-Dtest=BrokerJournalEvidenceTest,MorningDatabaseSessionTest#mdb2504001CurrentRunReferencePreservesExactIdentityAndRejectsForeignUuid')
    raw = raw.replace("'src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap','spotless:check','compile','jar:jar','install:install'", "'src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web','spotless:check','test-compile','jar:test-jar','jar:jar','install:install'")
    raw = raw.replace("env.update(JAVA_HOME=", "env.update(SCHUBERT_SHELLCHECK=str(b/'tools/shellcheck-0.11.0'),JAVA_HOME=")
    raw = raw.replace("'-Dmaven.repo.local='+str(repo)", "'-Dmaven.repo.local='+str(repo),'-Dnk.pt.node='+str(b/'tools/node-v24.19.0/bin/node')")
    raw = raw.replace("if c.attrib['name']=='dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration':coverage={q.attrib['type']:{k:int(q.attrib[k])for k in ['missed','covered']}for q in c.findall('counter')}", "if c.attrib['name']in ['dev/codex/schubert/nk/batch/platform/BrokerJournalEvidence','dev/codex/schubert/nk/batch/repository/MorningDatabaseSession','dev/codex/schubert/nk/batch/repository/MorningDatabaseSession$Session']:coverage[c.attrib['name']]={q.attrib['type']:{k:int(q.attrib[k])for k in ['missed','covered']}for q in c.findall('counter')}")
    raw = raw.replace('counts={};issues={};coverage={}', 'counts={};issues={};coverage={};method_scope={}')
    marker = "same=all(sha(source/p)==h for p,h in inputs.items())"
    extract = """x=ET.parse(source/'src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
for c in x.iter('class'):
 for method in c.findall('method'):
  key=c.get('name')+'#'+method.get('name')
  if key in TARGETS:
   require(key not in method_scope)
   method_scope[key]={q.get('type'):{'missed':int(q.get('missed')),'covered':int(q.get('covered'))}for q in method.findall('counter')}
validate_method_scope(method_scope)
"""
    raw = raw.replace(marker, extract + marker)
    raw = raw.replace("'classCounters':coverage", "'classCounters':coverage,'changedMethodScope':method_scope,'wholeClassFour100Accepted':False,'changedMethodScopeComplete':True")
    raw = raw.replace("set(counts)=={'dev.codex.schubert.nk.batch.file.'+n for n in ['CaddyPublicMetadataTest','CaddyPublicConfigurationTest','CaddyPublicCaMetadataTest','CaddyAddressBoundaryTest']}", "set(counts)=={'dev.codex.schubert.nk.batch.platform.BrokerJournalEvidenceTest','dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest'}")
    raw = raw.replace("counts['dev.codex.schubert.nk.batch.file.CaddyPublicMetadataTest']=={'tests':4,'failures':0,'errors':0,'skipped':0}", "counts['dev.codex.schubert.nk.batch.platform.BrokerJournalEvidenceTest']=={'tests':7,'failures':0,'errors':0,'skipped':0}and counts['dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest']=={'tests':1,'failures':0,'errors':0,'skipped':0}")
    raw = raw.replace('PG2504-selected-v1', 'PG2504-selected-v2').replace('source-selected-PG2504', 'source-selected-PG2504-v2').replace('PG2504-source.tar', 'PG2504-v2-source.tar')
    raw = 'TARGETS=' + repr(TARGETS) + '\n' + inspect.getsource(validate_method_scope) + '\n' + raw
    if check('HEAD=""\nARCHIVE_SHA=""\n' + raw, '<PG2504 actual changed Main selection>'):
        raise ValueError('actual full selected namespace required')
    compile(raw, '<PG2504 eight mandatory tests>', 'exec')
    return raw


def main():
    raw = inspect.getsource(transport.main).replace('PG2112', 'PG2504').replace('pg2112', 'pg2504')
    raw = raw.replace('pg2504-caddy-metadata-selected-v1', 'pg2504-strict-reference-selected-v2').replace('PG2504-source.tar', 'PG2504-v2-source.tar').replace('pg2504-caddy-selected.py', 'pg2504-strict-selected-v2.py')
    namespace = {**transport.__dict__, 'SERVER': server()}
    exec(compile(raw, '<PG2504 new-only selected transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
