"""Independent complete raw inverse for the three Test paths and all original19 methods/helpers."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG12192-audit-metric-source-post-v1'
PLAN_PIN='ca016a660ab8d1b8cff676b69b3d4be922e9494a41f87ea9855c749c85870c43'

def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def remove_one(tokens,declaration):
    positions=[i for i in range(len(tokens)-len(declaration)+1) if tokens[i:i+len(declaration)]==declaration]
    if len(positions)!=1:raise ValueError('one exact independent declaration required')
    i=positions[0];del tokens[i:i+len(declaration)]

def inverse(before,after,row):
    tokens=raw(after);old=raw(before)
    for c in row['constants']:
        remove_one(tokens,raw('private static final String '+c['name']+' = '+c['literal']+';'))
        if tokens.count(c['name'])!=c['references']:raise ValueError('all original literal references required')
        tokens=[c['literal'] if t==c['name'] else t for t in tokens]
    for original,current in row['identifierRenames'].items():
        if tokens.count(current)!=old.count(original) or original in tokens:raise ValueError('complete same-value field rename required')
        tokens=[original if t==current else t for t in tokens]
    if row['integerIndexConstant']:
        remove_one(tokens,raw('private static final int LOCKED_EVENT_INDEX = 2;'))
        if tokens.count('LOCKED_EVENT_INDEX')!=1:raise ValueError('one explicit locked index reference required')
        tokens=['2' if t=='LOCKED_EVENT_INDEX' else t for t in tokens]
    if tokens!=old:raise ValueError('all original raw assertions/helpers/case operations required')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    plan=data.read_checked(data.BASE/'PG12190-audit-metric-plan-v1/manifest.json',PLAN_PIN)
    normal=data.read_checked(data.BASE/'PG12164-audit-fixture-six-compile-v1/manifest.json','462a900efa1799ab71b9f192cb22f88c80aafcc8afd1453bffb2c577b0499048')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed={r['path'] for r in plan['sourceChanges']};assert len(changed)==3 and plan['rawDiagnosticsCorrected']==9 and plan['stringReferences']==40
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    negatives=0;catalog=[];tokens=0
    for row in plan['sourceChanges']:
        before=(snapshot/row['path']).read_text();after=(data.ROOT/row['path']).read_text()
        assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256']
        inverse(before,after,row);methods=re.findall(r'@Test\s+void (\w+)\(',before);assert len(methods)==row['originalMethods']
        catalog.extend(dict(path=row['path'],method=m) for m in methods);tokens+=len(raw(before))
        bads=[after.replace('@Test','@Disabled',1),after.replace('assertEquals(','assertNotEquals(',1)]
        for c in row['constants']:
            decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1
            bads.extend([after.replace(decl,'',1),after.replace(decl,decl.replace(c['literal'],'"wrong-fixture-value"'),1)])
        if row['constants']:
            c=row['constants'][0];m=[m for m in LEX.finditer(after) if m.group()==c['name']][-1];bads.append(after[:m.start()]+'"wrong-ref"'+after[m.end():])
        for current in row['identifierRenames'].values():
            m=[m for m in LEX.finditer(after) if m.group()==current][-1];bads.append(after[:m.start()]+'WRONG_FIELD_REF'+after[m.end():])
        if row['integerIndexConstant']:
            decl='private static final int LOCKED_EVENT_INDEX = 2;';assert after.count(decl)==1
            bads.extend([after.replace(decl,'',1),after.replace(decl,decl.replace('= 2','= 3'),1),after.replace('if (i == LOCKED_EVENT_INDEX)','if (i == 3)',1)])
        for bad in bads:
            assert bad!=after
            try:inverse(before,bad,row)
            except ValueError:negatives+=1
            else:raise AssertionError('changed oracle or fixture accepted')
    assert negatives==24 and len(catalog)==19
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PLAN_PIN,sourceChanges=plan['sourceChanges'],originalMethods=19,originalRawTokens=tokens,originalCatalog=catalog,metadataNegativeVectors=negatives,allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
