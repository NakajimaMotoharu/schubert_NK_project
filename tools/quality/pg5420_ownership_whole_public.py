"""Allowlisted original3896 XML projection and current-source summary; no test replay/signing."""
import ast
import hashlib
import json
import os
import sys
import pg5132_root_whole_public as previous
from pg5416_ownership_whole_qualification import SOURCE,ROOT,W,added_cases

SLOT='PG5414-current3896-cases'


def counts(raw):
    class Rebase(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value) is int and node.value in (3814,556,1654):
                return ast.copy_location(ast.Constant({3814:3896,556:562,1654:1664}[node.value]),node)
            return node
    return ast.unparse(ast.fix_missing_locations(Rebase().visit(ast.parse(raw))))


def export_source():
    return counts(previous.export_source().replace('PG5128','PG5414'))


def main_source():
    raw=previous.main_source()
    raw=raw.replace('pg5130-root-whole-qualified-v1','pg5416-ownership-whole-qualified-v1')
    raw=raw.replace('pg5132-root-case-projection-v1','pg5420-ownership-case-projection-v1')
    raw=raw.replace('PG5128','PG5414').replace('PG5130','PG5416').replace('PG5132_READ_ONLY','PG5420_READ_ONLY')
    return counts(raw)


def main():
    namespace={**vars(previous.previous),'SOURCE':SOURCE,'SLOT':SLOT,'export_source':export_source}
    exec(compile(main_source(),'<original3896 cases only>','exec'),namespace)
    return namespace['main']()


def new_case_trace(cases,selected,new):
    if selected['productionCandidateSource']!=SOURCE or selected['actualExit']!=0 or selected['tests']!=1164:
        raise ValueError('same current selected Test ID labels only, never reuse its result as whole result')
    by_method={(row['class'],row['method']):row for row in selected['cases']}
    physical={(row['class'],row['caseNameSha256']):row for row in cases}
    if len(physical)!=3896 or len(cases)!=3896:raise ValueError('all current projected XML physical case identities')
    trace=[]
    for cls,method in new:
        human=by_method[(cls,method)]
        if human['newIndependentCase'] is not True:raise ValueError('explicit independently specified new case label')
        actual=physical[(cls,hashlib.sha256(method.encode()).hexdigest())]
        if actual['result']!='PASS_ORIGINAL_XML':raise ValueError('new full result must come from original whole XML')
        trace.append({'testId':human['testId'],'wholeTestId':actual['testId'],'class':cls,
            'caseNameSha256':actual['caseNameSha256'],'sourceXml':actual['sourceXml'],
            'xmlSha256':actual['xmlSha256'],'result':'PASS_ORIGINAL_WHOLE_XML'})
    if len(trace)!=82 or len({row['testId'] for row in trace})!=82:raise ValueError('all82 new independent Test IDs exactly once')
    return trace


def publish_qualification():
    qualification=W/'pg5416-ownership-whole-qualified-v1/manifest.safe.json'
    raw=qualification.read_bytes();proof=json.loads(raw);value=proof['result']
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/SLOT
    projected=json.loads((out/'manifest.json').read_bytes())
    if not(type(proof['actualExit']) is int and proof['actualExit']==0 and proof['source']==SOURCE
        and value['productionSource']==SOURCE and value['tests']==3896 and value['suites']==562 and value['mainClasses']==1664
        and value['staticSixModules']==value['FESFlakyNotRun']==0 and value['allOriginalCaseIdentitiesRetained'] is True
        and value['allSixFormatBeforeAnyPt'] is True and projected['qualificationManifestSha256']==hashlib.sha256(raw).hexdigest()):
        raise ValueError('same original full and case projection qualification')
    selected_path=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/pg5404-process-query-green-v3-metadata-v2/manifest.json'
    if hashlib.sha256(selected_path.read_bytes()).hexdigest()!='f8efeee856df2c8eae87bd2f9113cc55e1101914726422ce24c8a225e8f3968d':
        raise ValueError('immutable source-qualified independent Test ID label reference')
    selected=json.loads(selected_path.read_bytes())
    trace=new_case_trace(json.loads((out/'cases.json').read_bytes()),selected,added_cases())
    keys=('productionSource','sourceSnapshot','sourceArchiveSha256','tests','suites','mainClasses','FESFlakyNotRun',
        'staticSixModules','allSixMainBuildsPassed','allSixFormatBeforeAnyPt','formatBeforePtProofSha256',
        'allOriginalCaseIdentitiesRetained','modules','coverage','jarHashes','allPhysicalMainSha256','changedClasses',
        'unchangedPhysicalClasses','oldNativeImported','candidateNativePending','F03Accepted','formalAccepted','global100','serverManifestSha256')
    result={key:value[key] for key in keys}
    result.update(deploymentHold=['BUG1414','YKT1178'],newSourceNativeQualified=False,wholeReplayed=False,
        newCaseTestIdTrace=trace,newCaseTestIdLabelSourceSha256=hashlib.sha256(selected_path.read_bytes()).hexdigest(),
        qualifiedSourceMatchesSelected=True,acceptedLeafDelta=0,effortPercent=None)
    with(out/'qualification.json').open('x') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'actualExit':0,'tests':3896,'mainClasses':1664,'newTestIdTrace':82,
        'sha256':hashlib.sha256((out/'qualification.json').read_bytes()).hexdigest(),'formalAccepted':False,'deploymentHeld':True}))


if __name__=='__main__':
    if sys.argv[1:]==['--qualification-summary']:publish_qualification()
    elif not sys.argv[1:]:main()
    else:raise SystemExit('known read-only projection mode required')
