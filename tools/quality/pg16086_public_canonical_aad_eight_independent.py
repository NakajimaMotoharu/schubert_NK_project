"""Independent public vector reconstruction and finite negative qualification; no Product rerun."""
import copy
import re
import struct
import unicodedata
import uuid
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST = ('PG16084-public-canonical-aad-eight-post-v1', '9604d48643df5cd54cea757bb49d1f504f097b0a2f83eff1f962671408d74be9')
OLD = ('PG16048-current2125-backup-request-registry-v1', '1481270818c601b5881b4f6e9fe55a9d4ac18e17e8a3698bf683161affdb71a9')
OUT = data.BASE / 'PG16086-public-canonical-aad-eight-independent-v1'
FIXTURE = 'tools/quality/architecture/PublicCanonicalAadValueTest.java'
FIXTURE_SHA = '9ba9b2009e7623821dc0a9d6bad223ed24b27d4005a761039dc2d551e03ec2d1'
NAMES = {'dev/codex/schubert/nk/api/idempotency/' + n for n in ('CanonicalField', 'ResponseSnapshotIdentity')}

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def read(pair):
    return data.read_checked(data.BASE / pair[0] / 'manifest.json', pair[1])

def lp(value):
    return struct.pack('>I', len(value)) + value

def expected(owner):
    fields = [b'api-inbox-response', b'schubert.request_inbox',
              uuid.UUID('00112233-4455-6677-8899-aabbccddeeff').bytes,
              bytes([1]), b'v1', b'QSSRSP01', b'001',
              b'' if owner is None else struct.pack('>q', owner)]
    return b''.join(lp(v) for v in fields)

def validate(value, old):
    require(type(value['actualExit']) is int and value['actualExit'] == 0 and value['source'] == SOURCE, 'same source actual0')
    require((value['tests'], value['suites'], value['newTestIds'], value['targetSourceUnits']) == (8, 1, 8, 2)
            and all(type(value[k]) is int for k in ('tests','suites','newTestIds','targetSourceUnits')), 'exact distinct fixture scope')
    require(all(type(value[k]) is int and value[k] == 0 for k in ('failures','errors','skipped','reruns','crcMismatch','forbiddenProductProbeHits','strictFour100GateExit')), 'no failed skipped timeout or probe')
    require(value['singleSession'] is True and value['sessionIdentity'] == 'PG16082-PUBLIC-CANONICAL-AAD-EIGHT', 'own session')
    require(value['coverageExecUnion'] is False if 'coverageExecUnion' in value else value['oldCoverageTransferred'] is False, 'no union')
    require(value['targetUnitFour100'] is value['completeSourceCoverageMeasured'] is value['allMeasuredApplicableCountersCovered'] is True, 'full coverage, not partial')
    require(value['manualCounterExclusions'] == value['metadataClasses'] == [] and value['officialGeneratedFiltersUnchanged'] is True, 'whole original filter')
    require(set(value['fullSourceUnits']) == set(value['executable']) == set(value['physicalClasses']) == NAMES, 'exact all Source and class')
    totals = {k:dict(missed=0,covered=0) for k in ('LINE','METHOD','CLASS','BRANCH')}
    for name in NAMES:
        unit = value['fullSourceUnits'][name]
        require(unit['physical'] == [name] and unit['four100'] is True, 'complete single physical class')
        require(unit['totals'] == value['executable'][name]['counters'], 'same actual counters')
        prior = old['fullSourceUnits'][name]
        for kind, counter in unit['totals'].items():
            require(type(counter['missed']) is int and type(counter['covered']) is int and counter['missed'] == 0 and counter['covered'] > 0, 'strict positive four')
            require(counter['covered'] == prior['counters'][kind]['covered'] + prior['counters'][kind]['missed'], 'same unexcluded denominator')
            totals[kind]['covered'] += counter['covered']
    require(value['totals'] == totals == {k:dict(missed=0,covered=n) for k,n in zip(('LINE','METHOD','CLASS','BRANCH'),(63,14,2,24))}, 'independent fixed total14 incl class initialization')
    require(value['onlyPublicCanonicalAndAadByteValues'] is value['newFixtureNotExtractedFromHeldTests'] is True
            and value['normalOrdinaryTestSourceDomain'] is False and (value['ownThreadCount'], value['ownTaskCount']) == (4,32), 'pure reviewed effects and domain')
    require(all(value[k] is False for k in ('cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualJdbcBackendConnected','actualFilesOpenedByProduct','rootMainInvoked','wholeF03Accepted','whole451Accepted','formalUpdated')), 'no unproved operation or acceptance')
    require(value['newAccepted'] == 0 and value['effortPercent'] is None, 'formal unchanged')

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p, old = read(POST), read(OLD)
    validate(p, old)
    fixture = (data.ROOT / FIXTURE).read_bytes()
    require(data.sha(fixture) == FIXTURE_SHA, 'reviewed eight fixture full hash')
    text = fixture.decode()
    names = re.findall(r'@Test\s+void\s+(public[0-9]{3}[A-Za-z0-9_]+)\s*\(', text)
    actual = []
    for file, pin in p['xmlHashes'].items():
        raw = (data.BASE / POST[0] / file).read_bytes()
        require(data.sha(raw) == pin, 'original XML hash')
        root = ET.fromstring(raw)
        require(all(root.get(k) == '0' for k in ('failures','errors','skipped')), 'all genuine pass')
        for node in root.findall('testcase'):
            require(not list(node), 'no skipped or failed case')
            actual.append((node.get('classname'), node.get('name')))
    require(len(actual) == len(set(actual)) == len(names) == 8
            and {n for c,n in actual} == set(names)
            and {c for c,n in actual} == {'dev.codex.schubert.nk.api.idempotency.PublicCanonicalAadValueTest'}, 'all exact unique Test IDs')
    prefix_text = text.split('private static final String AAD_PREFIX =',1)[1].split(';',1)[0]
    prefix = ''.join(re.findall(r'"([a-f0-9]+)"', prefix_text))
    literal = {'anonymous':bytes.fromhex(prefix + '00000000'),
               'minimum':bytes.fromhex(prefix + '000000080000000000000001'),
               'maximum':bytes.fromhex(prefix + '00000008000000e8d4a50fff')}
    oracle = {key:expected(owner) for key,owner in [('anonymous',None),('minimum',1),('maximum',999999999999)]}
    require(literal == oracle and list(map(len,oracle.values())) == [102,110,110], 'independent eight-LP big endian literal')
    require(unicodedata.normalize('NFC','e\u0301日本').encode().hex() == 'c3a9e697a5e69cac'
            and '"c3a9e697a5e69cac"' in text, 'independent NFC')
    require([str(n) for n in (-9223372036854775808,-1,0,9223372036854775807)] == ['-9223372036854775808','-1','0','9223372036854775807'], 'independent decimal')
    mutations = [
        ('source',lambda v:v.update(source='0'*40)),('exit-bool',lambda v:v.update(actualExit=False)),
        ('tests',lambda v:v.update(tests=7)),('bool-tests',lambda v:v.update(tests=True)),
        ('skipped',lambda v:v.update(skipped=1)),('failed',lambda v:v.update(failures=1)),
        ('rerun',lambda v:v.update(reruns=1)),('crc',lambda v:v.update(crcMismatch=1)),
        ('probe',lambda v:v.update(forbiddenProductProbeHits=1)),('session',lambda v:v.update(sessionIdentity='OLD')),
        ('union',lambda v:v.update(oldCoverageTransferred=True)),('coverage',lambda v:v.update(targetUnitFour100=False)),
        ('exclusion',lambda v:v.update(manualCounterExclusions=['one'])),('metadata',lambda v:v.update(metadataClasses=['one'])),
        ('filter',lambda v:v.update(officialGeneratedFiltersUnchanged=False)),('class',lambda v:v['physicalClasses'].pop(next(iter(NAMES)))),
        ('method',lambda v:v['fullSourceUnits'][next(iter(NAMES))]['totals']['METHOD'].update(missed=1)),
        ('total',lambda v:v['totals']['BRANCH'].update(covered=25)),
        ('secret',lambda v:v.update(actualSecretKeysLoaded=True)),('crypto',lambda v:v.update(cryptoOrKeyOperationsInvoked=True)),
        ('root',lambda v:v.update(rootMainInvoked=True)),('normal',lambda v:v.update(normalOrdinaryTestSourceDomain=True)),
        ('formal',lambda v:v.update(formalUpdated=True)),('accepted',lambda v:v.update(newAccepted=1)),
        ('effort',lambda v:v.update(effortPercent=100))]
    labels=[]
    for label,change in mutations:
        bad=copy.deepcopy(p);change(bad)
        try: validate(bad,old)
        except ValueError: labels.append(label)
        else: raise ValueError('false metadata accepted '+label)
    bads = [oracle['anonymous'][4:], oracle['minimum'][:-1], oracle['minimum'][:-8] + struct.pack('<q',1),
            oracle['anonymous'].replace(b'QSSRSP01',b'QSSRSP02'), oracle['anonymous'].replace(b'001',b'002')]
    require(len(bads) == 5 and all(b not in oracle.values() for b in bads), 'five distinct non-oracle mutations')
    for item in (p,old): verify(item['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'oracle.json',dict(aad={k:dict(length=len(v),hex=v.hex(),sha256=data.sha(v)) for k,v in oracle.items()},
                                    nfcHex='c3a9e697a5e69cac',expectedDecimal=['-9223372036854775808','-1','0','9223372036854775807']))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],
        fixtureSha256=FIXTURE_SHA,semanticNegativeVectors=len(labels),negativeLabels=labels,
        independentOracleNegativeVectors=5,oracleSha256=data.sha((OUT/'oracle.json').read_bytes()),
        tests=8,suites=1,onlyPublicCanonicalAndAadByteValues=True,newProductExecutions=0,
        normalOrdinaryTestSourceDomain=False,whole451Accepted=False,wholeF03Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
