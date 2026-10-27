"""Independent exact Java/integer-value inverse,45 source and27 integer-metadata negatives."""
from collections import Counter
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11104_web_pure_value_source_post import remove
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG11922-storage-attribute-fixture-source-post-v1'
PIN='510afeb4ee42cfa6dac9c4a737a7e1766932fb62e9b3d84d855fc03d2163301e'
JAVA=re.compile(r'0[bB][01_]+|0[0-7]+|[1-9][0-9_]*|(?:'+LEX.pattern+')',LEX.flags)

def lexical(text):
    return [m.group() for m in JAVA.finditer(text) if not m.group().startswith(('//','/*'))]

def integer_contract(row):
    if not re.fullmatch(r'0[0-7]+',row['literal']) or not re.fullmatch(r'0b[01]{3}(?:_[01]{3})*',row['replacement']):raise ValueError('explicit same-value integer bases required')
    if int(row['literal'],8)!=int(row['replacement'][2:].replace('_',''),2) or int(row['literal'],8)!=row['decimalValue']:raise ValueError('original octal and explicit binary values differ')

def inverse(before,after,rows):
    tokens=lexical(after);remove(tokens,lexical('private static final int TRANSFER_LIMIT_BYTES = 48_000_000;'))
    if tokens.count('TRANSFER_LIMIT_BYTES')!=1:raise ValueError('one independent transfer-size condition')
    tokens=['48_000_000' if t=='TRANSFER_LIMIT_BYTES' else t for t in tokens]
    for r in rows:
        if r['kind']!='STRING':continue
        remove(tokens,lexical('private static final String '+r['name']+' = '+r['literal']+';'))
        if tokens.count(r['name'])!=r['references']:raise ValueError('all original fixed attribute references required')
        tokens=[r['literal'] if t==r['name'] else t for t in tokens]
    modes=[r for r in rows if r['kind']=='MODE']
    for r in modes:integer_contract(r)
    mapping={r['replacement']:r['literal'] for r in modes};actual=Counter(t for t in tokens if t.startswith(('0b','0B')));expected=Counter(r['replacement'] for r in modes)
    if actual!=expected:raise ValueError('exact27 mode points and values required')
    tokens=[mapping.get(t,t) for t in tokens]
    if tokens!=lexical(before):raise ValueError('original raw mode/fixture/oracle/operation changed')

def main():
    invocation=capture(__file__);assert not OUT.exists();plan=data.read_checked(data.BASE/'PG11920-storage-attribute-fixture-plan-v1/manifest.json',PIN);normal=data.read_checked(data.BASE/'PG11894-session-json-fixture-six-compile-v1/manifest.json','3cc0fa3b71e348b8d5821b1269e616a69999c0c5467d6f7bb38c9b3cf69830e0');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;assert len(plan['sourceChanges'])==1;row=plan['sourceChanges'][0];path=row['path'];before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];inverse(before,after,row['constants']);assert len(re.findall(r'@Test\s+void ',before))==7;assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=path)
    bads=[after.replace('@Test','@Disabled',1)];strings=[r for r in row['constants'] if r['kind']=='STRING']
    for r in strings:
        decl='private static final String '+r['name']+' = '+r['literal']+';';assert after.count(decl)==1;bads += [after.replace(r['literal'],'"wrong-independent-attribute"',1),after.replace(decl,'',1)]
    first=strings[0];m=[m for m in JAVA.finditer(after) if m.group()==first['name']][-1];bads.append(after[:m.start()]+'"changed-reference"'+after[m.end():]);modes=[r for r in row['constants'] if r['kind']=='MODE'];points=[m for m in JAVA.finditer(after) if m.group().startswith('0b')];assert len(points)==27
    for m in points:
        value=m.group();bad=value[:-1]+('1' if value[-1]=='0' else '0');bads.append(after[:m.start()]+bad+after[m.end():])
    decl='private static final int TRANSFER_LIMIT_BYTES = 48_000_000;';m=[m for m in JAVA.finditer(after) if m.group()=='TRANSFER_LIMIT_BYTES'][-1];bads += [after.replace(decl,decl.replace('48_000_000','48_000_001'),1),after.replace(decl,'',1),after[:m.start()]+'48_000_001'+after[m.end():]]
    for old,new in [('48_000_001L','48_000_000L'),('assertTrue(Files.isSymbolicLink(link))','assertFalse(Files.isSymbolicLink(link))'),('new byte[] {1, 2, 3}','new byte[] {1, 2, 4}')]:assert old in after;bads.append(after.replace(old,new,1))
    assert len(bads)==45;negatives=0
    for bad in bads:
        assert bad!=after
        try:inverse(before,bad,row['constants'])
        except ValueError:negatives+=1
        else:raise AssertionError('changed independent mode/fixture/oracle accepted')
    integer_negatives=0
    for r in modes:
        bad=dict(r,decimalValue=r['decimalValue']^1)
        try:integer_contract(bad)
        except ValueError:integer_negatives+=1
        else:raise AssertionError('wrong integer-value metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PIN,sourceChanges=plan['sourceChanges'],stringConstants=5,stringReferences=55,modeLiteralPoints=27,boundConstants=1,originalMethods=7,metadataNegativeVectors=negatives,integerMetadataNegativeVectors=integer_negatives,rawJavaTokensRestored=len(lexical(before)),allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
