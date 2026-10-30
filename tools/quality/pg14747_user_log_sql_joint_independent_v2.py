"""Independent original34/new18/repeated16 accounting and zero held-probe dedicated SQL scope."""
import copy
import json
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg14742_user_log_sql_joint_thirty_four_pt as original

OUT=data.BASE/'PG14747-user-log-sql-joint-independent-v2'
PIN='4f4d6559dcc2ab58451504be29405129c71407d79d117274d3d23616c42093f7'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(v):return json.dumps(v,sort_keys=True)

def verify_raw_invocation(value):
    require(isinstance(value,dict) and 'invocation' not in value and isinstance(value.get('begin'),dict) and isinstance(value['begin'].get('invocation'),dict),'raw invocation belongs only to begin')
    verify(value['begin']['invocation'])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent SQL proof')
    p=data.read_checked(data.BASE/'PG14744-user-log-sql-joint-thirty-four-post-v1/manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG14742-user-log-sql-joint-thirty-four-pt-v1/manifest.json','48da91cf38cc557d00e76c66121aefa264b43c07e8c87b893efe610a76dbeec8')
    prior=data.read_checked(data.BASE/'PG14732-current842-incremental-registry-v1/manifest.json','aa96fcee286c5ca767581006cf4ed5803d3a9f72e0b9b2d961e79fabd235f096')
    require(p['actualExit']==raw['actualExit']==prior['actualExit']==0 and p['source']==raw['source']==prior['source']==original.SOURCE,'current actual receipts')
    declared=set()
    for name,path in original.TESTS.items():
        text=path.read_text();require(data.sha(path.read_bytes())==original.PINS[name],'frozen original whole Test')
        package=re.search(r'^package ([A-Za-z0-9_.]+);',text).group(1)
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text);require(len(methods)==original.COUNTS[name],'all original declarations')
        declared.update((package+'.'+name,m) for m in methods)
    observed=[]
    for filename,pin in p['xmlHashes'].items():
        value=(data.BASE/'PG14744-user-log-sql-joint-thirty-four-post-v1'/filename).read_bytes();require(data.sha(value)==pin,'original returned public XML bytes')
        doc=ET.fromstring(value);require(int(doc.get('tests'))==len(doc.findall('testcase')) and all(int(doc.get(k))==0 for k in ['failures','errors','skipped']),'actual XML FES0')
        for case in doc.findall('testcase'):
            require(not list(case),'no non-PASS XML');observed.append((case.get('classname'),case.get('name')))
    prior_cases={(v['classname'],v['name']) for v in prior['cases']};current=set(observed);new=current-prior_cases;repeated=current&prior_cases
    require(len(observed)==len(current)==34 and len({c for c,n in current})==5 and current==declared=={(v['classname'],v['name']) for v in raw['cases']},'whole34 in one original exec')
    require(len(new)==18 and len(repeated)==16 and all(c.endswith(('UserQuerySqlContractTest','LogSqlContractTest')) for c,n in new),'only SQL18 are new, plain16 necessary repeat')
    request_names={'dev/codex/schubert/nk/api/application/admin/UserQueryRequest','dev/codex/schubert/nk/api/application/log/LogRequest'}
    repo_names={'dev/codex/schubert/nk/api/persistence/UserQueryRepository','dev/codex/schubert/nk/api/persistence/LogQueryRepository'}
    require(set(p['fullSourceUnits'])==request_names|repo_names and set(p['physicalClasses'])==request_names|repo_names,'four entire one-class Source closures')
    require(all(p['fullSourceUnits'][n]['four100'] is True for n in request_names) and all(p['fullSourceUnits'][n]['four100'] is False for n in repo_names),'both requests full; repository error branches remain pending')
    stages=p['stages'];require(len(stages)==5 and all(s['actualExit']==0 and s['timedOut'] is False for s in stages),'all tool compile/selftest/probe/identity/coverage actual0')
    slot=data.ROOT.parent/'pgpt-runs/PG379/pg14744-user-log-sql-joint-thirty-four-post-v1'
    require((slot/'held-probe-self-test.stdout').read_text().strip()=='TOOL_METADATA_CHECKS=10' and (slot/'held-probe-audit.stdout').read_text().strip()=='FORBIDDEN_PROBE_HITS=0','actual own exec held probes0, not inferred')
    expected={k:p[k] for k in ['source','tests','suites','cases','xmlHashes','execSha256','completeSourceUnitClosure','fullSourceUnits','physicalClasses','executable','totals','owners','reportedEnvironment','sessionIdentity','crcMismatch']}
    def contract(value):
        require(all(wire(value[k])==wire(v) for k,v in expected.items()),'all verified actual semantic values fixed')
        require(value['tests']==34 and value['newCurrentSourceOriginalMethods']==18 and value['necessaryPreviouslyCountedOriginalMethods']==16,'new/repeated method roles exact')
        require(value['onlyReviewedPureValueSuites'] is False and value['onlyReviewedPublicJdbcInterfaceContracts'] is True and value['backendReceiverConstructed'] is True and value['actualJdbcBackendConnected'] is False,'real repository receiver, no real backend, no pure-only mislabel')
        require(type(value['forbiddenProductProbeHits']) is int and value['forbiddenProductProbeHits']==0 and value['heldProbeToolMetadataChecks']==10 and value['heldProbeHelperSha256']=='b0db809993acdc26b9e6f961c65ba4d92d19965a6221e555b924acc9171d547b','exact measured held-probe contract')
        require(value['priorProductResultsReused'] is value['oldCoverageTransferred'] is value['whole451Accepted'] is value['wholeF03Accepted'] is value['formalUpdated'] is False and value['newAccepted']==0 and value['effortPercent'] is None,'no old/whole/formal promotion')
        require(value['strictFour100GateExit']==1 and value['targetUnitFour100'] is False,'incomplete Repository retained')
    contract(p);labels=[]
    changes=[('source',lambda v:v.update(source='OLD')),('new-double',lambda v:v.update(newCurrentSourceOriginalMethods=34)),('repeat-erased',lambda v:v.update(necessaryPreviouslyCountedOriginalMethods=0)),('pure-label',lambda v:v.update(onlyReviewedPureValueSuites=True)),('receiver-erased',lambda v:v.update(backendReceiverConstructed=False)),('backend',lambda v:v.update(actualJdbcBackendConnected=True)),('probe-positive',lambda v:v.update(forbiddenProductProbeHits=1)),('probe-bool',lambda v:v.update(forbiddenProductProbeHits=False)),('scope',lambda v:v.update(fullSourceUnits={})),('coverage',lambda v:v.update(totals={})),('XML',lambda v:v.update(xmlHashes={})),('environment',lambda v:v.update(reportedEnvironment={})),('request-proof',lambda v:v['fullSourceUnits'][next(iter(request_names))].update(four100=False)),('repo-pass',lambda v:v['fullSourceUnits'][next(iter(repo_names))].update(four100=True)),('old',lambda v:v.update(oldCoverageTransferred=True)),('formal',lambda v:v.update(formalUpdated=True)),('effort',lambda v:v.update(effortPercent=50)),('strict',lambda v:v.update(strictFour100GateExit=0))]
    for label,change in changes:
        bad=copy.deepcopy(p);change(bad)
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false SQL contract accepted '+label)
    verify_raw_invocation(raw)
    raw_role_negatives=[]
    for label,change in [('missing',lambda v:v['begin'].pop('invocation')),('moved',lambda v:v.update(invocation=v['begin'].pop('invocation'))),('ambiguous',lambda v:v.update(invocation=v['begin']['invocation'])),('wrong-begin-type',lambda v:v.update(begin=None))]:
        bad=copy.deepcopy(raw);change(bad)
        try:verify_raw_invocation(bad)
        except ValueError:raw_role_negatives.append(label)
        else:raise ValueError('wrong raw invocation role admitted '+label)
    for value in [p,prior]:verify(value['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,rawSha256='48da91cf38cc557d00e76c66121aefa264b43c07e8c87b893efe610a76dbeec8',previousRegistrySha256='aa96fcee286c5ca767581006cf4ed5803d3a9f72e0b9b2d961e79fabd235f096',originalXmlMethods=34,originalXmlSuites=5,newUniqueMethods=18,necessaryRepeatedMethods=16,newCases=[dict(classname=c,name=n) for c,n in sorted(new)],repeatedCases=[dict(classname=c,name=n) for c,n in sorted(repeated)],fullRequestSourcePrograms=sorted(request_names),incompleteRepositorySourcePrograms=sorted(repo_names),forbiddenProductProbeHits=0,heldProbeToolMetadataChecks=10,semanticNegativeVectors=len(labels),negativeLabels=labels,rawInvocationRoleNegativeVectors=len(raw_role_negatives),rawInvocationRoleNegativeLabels=raw_role_negatives,bug='BUG-2112',ykt='YKT-1859',coverageExecUnion=False,oldSourceTransferred=False,productTestsReexecutedByPost=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
