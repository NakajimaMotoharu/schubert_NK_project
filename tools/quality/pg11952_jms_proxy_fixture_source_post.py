"""Independent strict raw inverse of12 original JMS methods with40 malformed-source vectors."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify
OUT=data.BASE/'PG11952-jms-proxy-fixture-source-post-v1'
PLAN='2b369e6aac93aca17dc3685af29868996c0467c81a49e42be96bbbbbc44a315a'
def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
def inverse(before,after,rows):
    tokens=raw(after)
    for row in rows:
        declaration=raw('private static final String '+row['name']+' = '+row['literal']+';');positions=[i for i in range(len(tokens)-len(declaration)+1) if tokens[i:i+len(declaration)]==declaration]
        if len(positions)!=1:raise ValueError('one exact same-value declaration required')
        i=positions[0];del tokens[i:i+len(declaration)]
        if tokens.count(row['name'])!=row['references']:raise ValueError('all exact independent references required')
        tokens=[row['literal'] if t==row['name'] else t for t in tokens]
    if tokens!=raw(before):raise ValueError('full original raw token inventory required')
def main():
    invocation=capture(__file__);assert not OUT.exists();plan=data.read_checked(data.BASE/'PG11950-jms-proxy-fixture-plan-v1/manifest.json',PLAN);normal=data.read_checked(data.BASE/'PG11924-storage-attribute-fixture-six-compile-v1/manifest.json','6c9f579aa08c720ce523423efa8ca7dc64a941dac559a548927259f09f28555c');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==2;assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed);negative=0;token_count=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();assert data.sha(after.encode())==row['sha256'] and data.sha(before.encode())==row['beforeSha256'];inverse(before,after,row['constants']);assert len(re.findall(r'@Test\s+void ',before))==6;token_count+=len(raw(before));bads=[after.replace('@Test','@Disabled',1)]
        for c in row['constants']:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1;bads.extend([after.replace(decl,'',1),after.replace(decl,decl.replace(c['literal'],'"wrong-fixed-field"'),1)])
        c=row['constants'][0];m=[m for m in LEX.finditer(after) if m.group()==c['name']][-1];bads.append(after[:m.start()]+'"wrong-reference"'+after[m.end():]);needle='new byte[] {1, 2, 3}' if 'GuardTest' in row['path'] else 'new byte[280]';assert needle in after;bads.append(after.replace(needle,needle.replace('3}','4}').replace('3}', '4}').replace('280','281').replace('2, 3','2, 4'),1))
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row['constants'])
            except ValueError:negative+=1
            else:raise AssertionError('changed field/oracle or disabled method accepted')
    assert negative==40;verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PLAN,sourceChanges=plan['sourceChanges'],originalMethods=12,originalRawTokens=token_count,metadataNegativeVectors=negative,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
