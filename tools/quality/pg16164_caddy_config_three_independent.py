"""Independent fixed-profile/template and XML checks; no Product or previous test rerun."""
import copy
import ipaddress
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG16162-caddy-config-three-post-v1','241833934d3a7e7779b84a9515f1390799e348eb0a47eb002668245dea2f1bed')
RAW=('PG16160-caddy-config-three-pt-v1','4fa248ef2e84f438988379450ec7ba5d4f8958588e834140667da6bd3a802a83')
PREVIOUS=('PG16088-current2133-canonical-aad-registry-v1','b6e7dc918a723fd30965322bc8400e51a786872204ea72a99f3e9b18534e30b7')
OUT=data.BASE/'PG16164-caddy-config-three-independent-v1'
NAME='dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration'
CLASS='dev.codex.schubert.nk.batch.file.CaddyPublicConfigurationTest'
EXPECTED={'caddy455006Ipv4Ipv6AndFormattingRemainTlsOnly','caddy455007AnyUnexpectedDirectiveOrAddressFailsClosed','caddy455008DeploymentTemplateMatchesIndependentDirectiveSet'}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in (POST,RAW,PREVIOUS)]
    require(p['actualExit']==raw['actualExit']==old['actualExit']==0 and p['source']==raw['source']==old['source']==SOURCE,'same actual source')
    local=[]
    for name,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/name).read_bytes();require(data.sha(blob)==pin,'original copied XML')
        root=ET.fromstring(blob);require(root.get('name')==CLASS and root.get('tests')=='3'
                and all(root.get(k)=='0' for k in ('failures','errors','skipped')),'allthree notpartial')
        for case in root.findall('testcase'):
            require(not list(case),'no skipped or failed');local.append((case.get('classname'),case.get('name')))
    require(len(local)==len(set(local))==3 and set(local)=={(CLASS,n) for n in EXPECTED}
            and not set(local)&{(v['classname'],v['name']) for v in old['cases']},'three genuinely new original cases')
    test=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CaddyPublicConfigurationTest.java'
    text=test.read_text();require(data.sha(text.encode())=='a7cde1d1a189e6e835084e612d83e87b0d51925a8a17374f97005301019daa9c','unchanged original')
    require(set(re.findall(r'@Test\s+void\s+(\w+)\(',text))==EXPECTED and text.count('Files.readString(')==1,'whole3/one public read')
    match=re.search(r'String GOLDEN =\s*"""\n(.*?)\n\s*""";',text,re.S);require(match is not None,'explicit independent golden')
    golden='\n'.join(line.strip() for line in match.group(1).splitlines() if line.strip())
    template=data.ROOT/'src/deployment/caddy/Caddyfile.template';blob=template.read_bytes()
    require(data.sha(blob)=='2914bfd4134186911562071f92652ce750e513213a749672dd161615c3d8763c'
            and subprocess.check_output(['git','show',SOURCE+':src/deployment/caddy/Caddyfile.template'],cwd=data.ROOT)==blob,'source template independent original/current')
    def template_contract(value):
        normalized='\n'.join(line.strip() for line in value.splitlines() if line.strip() and not line.strip().startswith('#'))
        require(normalized.replace('<GLOBAL_IP>','127.0.0.1')==golden,'full explicit directive equality')
    template_contract(blob.decode());oracle=[]
    for before,after in [('admin off','admin localhost:2019'),('max_size 2MB','max_size 10MB'),('https://','http://'),(':55160',':55161'),('response_header_timeout 30s','response_header_timeout 31s')]:
        require(before in blob.decode(),'nondegenerate oracle vector')
        try:template_contract(blob.decode().replace(before,after))
        except ValueError:oracle.append(before)
        else:raise ValueError('false directive accepted')
    require(ipaddress.ip_address('255.255.255.255').packed==bytes([255]*4) and ipaddress.ip_address('2001:db8::1').version==6,'numeric literal interpretation independent')
    design='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'
    approved=(data.ROOT/design).read_bytes();require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT)
            and all(v in approved.decode() for v in ['55160','literal IPv4又はbracket付きIPv6','root:caddy0640']),'approved source profile, not live deployment')
    expected_counts={'LINE':dict(covered=24,missed=109),'METHOD':dict(covered=2,missed=21),'CLASS':dict(covered=1,missed=0),'BRANCH':dict(covered=22,missed=78)}
    def contract(value):
        require(type(value['actualExit']) is int and value['actualExit']==0 and value['source']==SOURCE and value['originalManifestSha256']==RAW[1],'original genuine terminal')
        require((value['tests'],value['suites'],value['newTestIds'],value['newAccepted'])==(3,1,0,0) and wire(value['cases'])==wire(raw['cases']),'exact new cases not added assertions')
        require(value['totals']==expected_counts and value['fullSourceUnits'][NAME]['totals']==expected_counts
                and value['completeSourceUnitClosure']=={NAME:[NAME]} and value['metadataClasses']==[],'allSource denominator')
        require(value['singleSession'] is True and value['crcMismatch']==0 and value['execSha256']==raw['execSha256']
                and value['sessionIdentity']=='PG16160-ORIGINAL-CADDY-CONFIG-THREE','one own session')
        require(value['targetUnitFour100'] is False and value['allMeasuredApplicableCountersCovered'] is False
                and value['strictFour100GateExit']==1 and value['manualCounterExclusions']==[],'partial kept partial')
        require(value['originalTestPublicTemplateRead'] is value['actualFilesOpenedByProduct'] is value['normalOrdinaryTestSourceDomain'] is True,'explicit real public template read')
        require(all(value[k] is False for k in ['actualPrivateFilesOpened','actualDnsRequestsIssued','cryptoOrKeyOperationsInvoked',
                'actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','rootMainInvoked',
                'priorProductResultsReused','oldCoverageTransferred','formalUpdated','whole451Accepted'])
                and value['effortPercent'] is None,'no native/old result/secret acceptance')
        require(value['templateBinding']['originalSha256']=='2914bfd4134186911562071f92652ce750e513213a749672dd161615c3d8763c'
                and value['templateBinding']['externalDeploymentChanged'] is False,'exclusive public fixture only')
    contract(p);negative=[]
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('tests','tests',4),('suites','suites',2),
        ('cases','cases',[]),('totals','totals',{}),('closure','completeSourceUnitClosure',{}),('metadata','metadataClasses',['X']),
        ('crc','crcMismatch',1),('session','singleSession',False),('exec','execSha256','0'*64),('four','targetUnitFour100',True),
        ('applicable','allMeasuredApplicableCountersCovered',True),('strict','strictFour100GateExit',0),('exclusion','manualCounterExclusions',['X']),
        ('file','actualFilesOpenedByProduct',False),('template','originalTestPublicTemplateRead',False),('private','actualPrivateFilesOpened',True),
        ('dns','actualDnsRequestsIssued',True),('crypto','cryptoOrKeyOperationsInvoked',True),('keys','actualSecretKeysLoaded',True),
        ('Root','rootMainInvoked',True),('union','oldCoverageTransferred',True),('formal','formalUpdated',True),('effort','effortPercent',100)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(label)
        else:raise ValueError('false Caddy result '+label)
    require(len(negative)==25 and len(oracle)==5,'finite metadata/oracle negatives')
    require(all(old['fullSourceUnits'][NAME]['counters'][k]['covered']>=expected_counts[k]['covered']
                for k in expected_counts),'old proof kept, no exec union or weaker replacement')
    for v in (p,raw,old):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=3,
        semanticNegativeVectors=25,negativeLabels=negative,independentOracleNegativeVectors=5,oracleLabels=oracle,
        previousSourceProofs={NAME:old['fullSourceUnits'][NAME]},previousSourceProofsNotReplaced=True,
        newSourcePrograms=0,publicTemplateSha256=data.sha(blob),approvedDesignSha256=data.sha(approved),
        actualPublicTemplateRead=True,actualPrivateFilesRead=False,productTestsReexecuted=0,newAccepted=0,
        formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
