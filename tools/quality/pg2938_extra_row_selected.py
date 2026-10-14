"""Whole seven failed-pair tests, exact same Main and independent target-class counters."""
import inspect
import json
from pyflakes.api import check
import pg2916_failed_pair_boundary_selected as prior

FILES=[*prior.FILES,'tools/quality/vm/050_s1/NativeCoverageXml471.java']


def server():
    raw=prior.server().replace('PG2916','PG2938').replace('source-full-PG2798','source-full-PG2930')
    before="'-cp',str(classes)+':'+cp,'SelectedClassContractLauncher'"
    after="'-javaagent:'+str(repo/'org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar')+'=destfile='+str(out/'selected.exec')+',append=false','-cp',str(classes)+':'+cp,'SelectedClassContractLauncher'"
    if raw.count(before)!=1:raise ValueError('one real JUnit agent boundary required')
    raw=raw.replace(before,after)
    extra="""hosts=[]
for module in ['protocol','storage','bootstrap','api','web','batch']:
 p=source/'src'/('schubert-nk-'+module)/'target/jacoco.exec'
 require(sha(p)==INPUT['baseFull']['qualificationInputs'][module]['exec']);hosts.append(str(p))
coverage_xml=out/'target-coverage.xml'
execute('target-coverage',[str(jdk/'java'),'-cp',str(classes)+':'+cp,'NativeCoverageXml471',jars[-1],str(coverage_xml),*hosts,str(out/'selected.exec')],90)
tree=ET.parse(coverage_xml).getroot();target=[c for c in tree.findall('.//class')if c.get('name')=='dev/codex/schubert/nk/batch/repository/BackupFailureSnapshot']
require(len(target)==1)
counters={c.get('type'):{k:int(c.get(k))for k in ['missed','covered']}for c in target[0].findall('counter')}
require(all(counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']))
"""
    marker="result={'actualExit':0,'candidateSource'"
    if raw.count(marker)!=1:raise ValueError('one exact target counter boundary required')
    raw=raw.replace(marker,extra+marker)
    raw=raw.replace("'coverageClaim':False,'nativeImported'","'coverageClaim':False,'targetClassFour100':True,'targetCounters':counters,'coverageXmlSha256':sha(coverage_xml),'selectedExecSha256':sha(out/'selected.exec'),'nativeImported'")
    if check('INPUT={}\n'+raw,'<whole target seven and class counters>'):raise ValueError('complete graph required')
    compile(raw,'<same Main target branch counter>','exec');return raw


def main():
    raw=prior.transport_body().replace('pg2916-failed-pair-boundary-selected-v1','pg2938-extra-row-selected-v1').replace('pg2800-jdbc-null-fixed-full-qualified-v1','pg2932-format-fixed-full-qualified-v1').replace('3680','3684')
    marker="libraries=dict(old['libraries'])"
    extra="""libraries=dict(old['libraries'])
    native=json.loads((W/'pg2934-format-fixed-same-native-qualified-v1/input.safe.json').read_bytes())
    libraries.update(native['libraries'])"""
    if raw.count(marker)!=1:raise ValueError('one exact analyzer dependency namespace required')
    raw=raw.replace(marker,extra)
    ns={**prior.prior.prior.__dict__,'FILES':FILES,'TEST':prior.TEST,'SLOT':'PG2938-candidate-v1','SERVER':server()}
    exec(compile(raw,'<exact seven Test-only inputs>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
