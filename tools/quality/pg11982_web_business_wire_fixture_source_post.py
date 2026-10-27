"""Strict original8 raw inverse, two exact field bindings and52 metadata/oracle negatives."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify
OUT=data.BASE/'PG11982-web-business-wire-fixture-source-post-v1'
PIN='4b268d5e51e5688ef8ee69f35b18000609a344d15e07548cdffac4b0cecaf046'
def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
def inverse(before,after,row):
    tokens=raw(after)
    for c in row['constants']:
        decl=raw('private static final String '+c['name']+' = '+c['literal']+';');positions=[i for i in range(len(tokens)-len(decl)+1) if tokens[i:i+len(decl)]==decl]
        if len(positions)!=1:raise ValueError('one exact independent same-value String required')
        i=positions[0];del tokens[i:i+len(decl)]
        if tokens.count(c['name'])!=c['references']:raise ValueError('all original literal reference bindings required')
        tokens=[c['literal'] if t==c['name'] else t for t in tokens]
    for f in row['renames']:
        if tokens.count(f['newName'])!=f['bindings'] or f['oldName'] in tokens:raise ValueError('exact two field bindings required')
        tokens=[f['oldName'] if t==f['newName'] else t for t in tokens]
    if tokens!=raw(before):raise ValueError('full original fixture/oracle/assertion/method token inventory required')
def main():
    invocation=capture(__file__);assert not OUT.exists();plan=data.read_checked(data.BASE/'PG11980-web-business-wire-fixture-plan-v1/manifest.json',PIN);normal=data.read_checked(data.BASE/'PG11954-jms-proxy-fixture-six-compile-v1/manifest.json','9914ca39739520420fbad05428dbf20ef4c776998175713a838b4ca0ab1b6824');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;assert len(plan['sourceChanges'])==1;row=plan['sourceChanges'][0];before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text();assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=row['path']);inverse(before,after,row);assert len(re.findall(r'@Test\s+void ',before))==8;bads=[]
    for c in row['constants']:
        decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1;bads += [after.replace(decl,'',1),after.replace(decl,decl.replace(c['literal'],'"wrong-literal-vector"'),1)]
    for f in row['renames']:
        ts=[m for m in LEX.finditer(after) if m.group()==f['newName']];assert len(ts)==2
        for m in ts:bads.append(after[:m.start()]+'FOREIGN_LENGTH_TABLE'+after[m.end():])
    c=row['constants'][0];m=[m for m in LEX.finditer(after) if m.group()==c['name']][-1];bads += [after[:m.start()]+'"changed-reference"'+after[m.end():],after.replace('@Test','@Disabled',1),after.replace('n < 180','n < 179',1),after.replace('task.get(10, TimeUnit.SECONDS)','task.get(9, TimeUnit.SECONDS)',1)];assert len(bads)==52
    for bad in bads:
        assert bad!=after
        try:inverse(before,bad,row)
        except ValueError:pass
        else:raise AssertionError('unequal source/oracle/field/worker/deadline accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PIN,sourceChanges=plan['sourceChanges'],stringConstants=22,stringReferences=plan['stringReferences'],renamedFields=2,renamedBindings=4,originalMethods=8,originalRawTokens=len(raw(before)),metadataNegativeVectors=len(bads),allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
