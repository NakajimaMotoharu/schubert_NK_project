"""Read original3900 XML only; explicit new-four identities, no test replay."""
import ast
import hashlib
import json
import os
import sys
import pg5420_ownership_whole_public as previous
from pg5552_snapshot_whole_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED,added_cases

SLOT='PG5550-current3900-cases'


def counts(raw):
    class Rebase(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3896,562):
                return ast.copy_location(ast.Constant({3896:3900,562:563}[node.value]),node)
            return node
    return ast.unparse(ast.fix_missing_locations(Rebase().visit(ast.parse(raw))))


def export_source():return counts(previous.export_source().replace('PG5414','PG5550'))


def main_source():
    raw=previous.main_source().replace('pg5416-ownership-whole-qualified-v2',QUALIFIED)
    raw=raw.replace('pg5420-ownership-case-projection-v1','pg5558-snapshot-case-projection-v1')
    raw=raw.replace('PG5414','PG5550').replace('PG5416','PG5552').replace('PG5420_READ_ONLY','PG5558_READ_ONLY')
    return counts(raw)


def main():
    namespace={**vars(previous.previous.previous),'SOURCE':SOURCE,'SLOT':SLOT,'export_source':export_source}
    exec(compile(main_source(),'<original3900 public allowlist>','exec'),namespace)
    return namespace['main']()


def publish_qualification():
    path=W/QUALIFIED/'manifest.safe.json';raw=path.read_bytes();proof=json.loads(raw);value=proof['result']
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/SLOT
    projected=json.loads((out/'manifest.json').read_bytes());cases=json.loads((out/'cases.json').read_bytes())
    if not(type(proof['actualExit'])is int and proof['actualExit']==0 and proof['source']==SOURCE
        and(value['tests'],value['suites'],value['mainClasses'])==(3900,563,1664)
        and value['staticSixModules']==value['FESFlakyNotRun']==0 and value['allOriginalCaseIdentitiesRetained']is True
        and value['allSixFormatBeforeAnyPt']is True and projected['qualificationManifestSha256']==hashlib.sha256(raw).hexdigest()
        and len(cases)==3900):raise ValueError('exact original3900 whole, not arithmetic credit')
    trace=[]
    for cls,name in added_cases():
        matches=[r for r in cases if r['class']==cls and r['caseNameSha256']==hashlib.sha256(name.encode()).hexdigest()]
        if len(matches)!=1 or matches[0]['result']!='PASS_ORIGINAL_XML':raise ValueError('each source-added method must be present exactly once in original whole XML')
        trace.append({'class':cls,'method':name,**matches[0]})
    if len(trace)!=4:raise ValueError('exact four independently specified new scratch cases')
    keys=('productionSource','sourceSnapshot','sourceArchiveSha256','tests','suites','mainClasses','FESFlakyNotRun',
        'staticSixModules','allSixMainBuildsPassed','allSixFormatBeforeAnyPt','formatBeforePtProofSha256',
        'allOriginalCaseIdentitiesRetained','modules','coverage','jarHashes','allPhysicalMainSha256','changedClasses',
        'unchangedPhysicalClasses','oldNativeImported','candidateNativePending','F03Accepted','formalAccepted','global100','serverManifestSha256')
    result={key:value[key]for key in keys}
    result.update(newCaseTestIdTrace=trace,wholeReplayed=False,newSourceNativeQualified=False,acceptedLeafDelta=0,effortPercent=None)
    with(out/'qualification.json').open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'tests':3900,'suites':563,'mainClasses':1664,'newTestIdTrace':4,
        'sha256':hashlib.sha256((out/'qualification.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':
    if sys.argv[1:]==['--qualification-summary']:publish_qualification()
    elif not sys.argv[1:]:main()
    else:raise SystemExit('known read-only publication mode required')
