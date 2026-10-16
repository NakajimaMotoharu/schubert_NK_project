"""Original full XML, all old identities and exact closed three-entry physical difference."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import copy,run
import pg4422_shared_manager_whole_qualification as template
from pg4694_ssc299_full import SOURCE,ROOT,W

SLOT='pg4696-ssc299-whole-qualified-v1'
PREFIX='dev.codex.schubert.nk.batch.file.'
ADDED={
 'RootStartupPendingTest':['exactBothServicesMatchOnlyTheRecordedChildGeneration','eachIndependentForeignIdentityAndOtherServiceIsRejected','absentBoundaryObjectsFailBeforeAnyNativeAuthority'],
 'RootServiceEnvironmentTest':['eachServiceExportsExactlyFiveLiteralBindingsAndNoInheritedExtras','missingWrongServiceRelativeAndExtraSuffixCredentialPathsAreRejected','absentOrForeignSelfFailsBeforeReadingAnyCredentialLocation'],
 'ExternalEntryRejectionTest':['rootArgumentErrorsExitSeventyBeforeAnyAdmission','evenExactApiWebArgumentsCannotAcquireOsOwnershipFromAnOrdinaryJvm','malformedMorningAndCleanupArgumentsNeverSelectBusinessWork'],
 'RootServiceProofTest':['eachIndependentEpochBootAndActivationContradictionNeverEmitsProof'],
 'MainTerminationPortTest':['morningRequestsLiteralSuccessWarningOnlyAfterTypedBusinessReturn','morningMalformedKnownAndUnknownFailuresNeverInventSuccessfulExit','rootRetainsSameMeasurementThroughAdmissionTerminalThenNonReadyExit','rootBadArgsAndUnavailableMeasurementCannotReachNativeAdmission','rootCaptureAndUnknownAdmissionFailureNeverBecomeExitRequest','cleanupSelectsOnlyExactExpiryAndRequestsLiteralNormalizedStatusOnce','cleanupInvalidKnownUnknownAndNullArgumentsPreserveFailureContract','constructorNullsAndTerminationFailuresNeverEnableAlternatePublicEntry']}
NEW_CASES=[(PREFIX+cls,method)for cls,methods in ADDED.items()for method in methods]
FAMILY='batch:dev/codex/schubert/nk/batch/file/'
MODIFIED={FAMILY+n+'.class'for n in ['RootServiceLauncher','RootServiceLauncher$1','MorningProcessMain','MorningProcessMain$1','MorningProcessMain$Archive','CleanupProcessMain']}
INTERFACES={FAMILY+'RootServiceLauncher$'+n+'.class'for n in ['Measurement','NativeAdmission']}


def physical_difference(old,new,candidate):
    import re
    if any(type(m)is not dict or any(type(k)is not str or type(v)is not str or re.fullmatch('[a-f0-9]{64}',v)is None for k,v in m.items())for m in [old,new,candidate]):raise ValueError('strict actual SHA256 inventories')
    if len(old)!=1644 or len(new)!=1646 or set(new)!=set(old)|INTERFACES or new!=candidate:raise ValueError('all1646 exact same-source inventory and two internal interface declarations required')
    changed={k for k in old if old[k]!=new[k]}
    if changed!=MODIFIED:raise ValueError('only registered six physical classes in three entry families differ')
    values=[{'oldClass':k,'class':k,'oldSha256':old[k],'newSha256':new[k],'action':'MODIFIED'}for k in sorted(changed)]
    values.extend({'oldClass':None,'class':k,'oldSha256':None,'newSha256':new[k],'action':'ADDED_INTERNAL_INTERFACE'}for k in sorted(INTERFACES))
    return values,len(old)-len(changed)


def qualifier_source():
    raw=inspect.getsource(template.qualify).replace("old = base / 'runs/PG3966-six-v1'","old = base / 'runs/PG4420-six-v1'")
    raw=raw.replace('PG4420-six-v1','PG4694-six-v1',1).replace('source-full-PG4420','source-full-PG4694').replace('transfer/PG4420-source.tar','transfer/PG4694-source.tar')
    raw=raw.replace('len(additions) == 4','len(additions) == 18')
    raw=raw.replace('actual qualified old3717 baseline manifest','actual qualified old3721 baseline manifest').replace('all3717 exact aliases retained plus four independent methods','all3721 original identities retained plus eighteen independently specified methods')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in {3717,3721,545,1644}:return ast.copy_location(ast.Constant({3717:3721,3721:3739,545:549,1644:1646}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    first=raw.index('    moves = {');last=raw.index("    need(all((sha(source / n)",first)
    raw=raw[:first]+"    modifications, immutable = physical_difference(oldphysical, physical, data['candidateMain'])\n"+raw[last:]
    return raw


def main():
    original=json.loads((W/'pg4694-ssc299-six-v1/manifest.safe.json').read_bytes())
    if original['actualExit']!=0 or original['source']!=SOURCE:raise ValueError('original genuine whole0 required, never replay')
    selected=W/'pg4690-entry-termination-selected-v1';selected_result=json.loads((selected/'manifest.safe.json').read_bytes())
    if selected_result['actualExit']!=0 or selected_result['sourceSnapshot']!=SOURCE:raise ValueError('genuine same candidate78 selected first')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT):raise ValueError('entire fixed source/Test/settings unchanged')
    candidate={}
    for module in ['protocol','storage','bootstrap','api','web','batch']:
        classes=selected/'source'/('src/schubert-nk-'+module+'/target/classes')
        candidate.update({module+':'+str(p.relative_to(classes)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(classes.rglob('*.class'))})
    prior=json.loads((W/'pg4428-shared-manager-whole-qualified-v1/manifest.safe.json').read_bytes())['result']
    physical_difference(prior['allPhysicalMainSha256'],candidate,candidate)
    before=json.loads((W/'pg4694-ssc299-six-v1/begin.safe.json').read_bytes())
    data={'source':SOURCE,'priorManifestSha256':prior['serverManifestSha256'],'priorJarHashes':prior['jarHashes'],'archiveSha256':before['archiveSha256'],'aliases':{},'newCases':NEW_CASES,'candidateMain':candidate,'allMainSourceSha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw='import json\nMODIFIED=set('+repr(sorted(MODIFIED))+')\nINTERFACES=set('+repr(sorted(INTERFACES))+')\n'+inspect.getsource(physical_difference)+'\n'+qualifier_source()+'\nprint(json.dumps(qualify('+repr(data)+')))\n'
    from pyflakes.api import check
    if check(raw,'<whole fixed SSC299 independent qualifier>'):raise ValueError('all actual standalone globals')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'qualify.private.py';path.write_text(raw);digest=hashlib.sha256(raw.encode()).hexdigest()
    remote='/home/mini/schubert-nk-pgpt/transfer/PG4696-whole-qualified-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new-only qualification namespace')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed qualification transfer')
    command='python3 -B '+remote+'/qualify.private.py'
    if len(command.encode())>=256:raise ValueError('fixed short command required')
    code,output=run('sha256sum '+remote+'/qualify.private.py',timeout=30)
    if code or output.split()[0]!=digest:raise ValueError('entire fixed payload bytes')
    code,output=run(command,timeout=180);(out/'observer.private.log').write_text(output)
    value={'actualExit':code,'source':SOURCE,'payloadSha256':digest,'formalAccepted':False,'wholeReplayed':False}
    if code==0:value['result']=json.loads(next(line for line in reversed(output.splitlines())if line.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in ['tests','suites','mainClasses','staticSixModules','unchangedPhysicalClasses','global100','F03Accepted']}))
    return code


if __name__=='__main__':raise SystemExit(main())
