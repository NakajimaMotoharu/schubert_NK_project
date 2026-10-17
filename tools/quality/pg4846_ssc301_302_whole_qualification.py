"""Original full XML/3739 retained cases/22 additions/exact two Main plus declaration delta."""
import ast
import inspect
import pg4696_ssc299_whole_qualification as previous
from pg4844_ssc301_302_full import SOURCE,ROOT,W

SLOT='pg4846-ssc301-302-whole-qualified-v1'
MODIFIED={'api:dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.class','batch:dev/codex/schubert/nk/batch/file/CleanupExpiryExecution.class'}
INTERFACES={'api:dev/codex/schubert/nk/api/bootstrap/ApiProcessMain$ConfigurationLoad.class'}
API=['ssc301001SameValuesAndIndependentCanonicalGolden','ssc301002RealMalformedLoaderMapsOnlyToFixed70','ssc301003AlgorithmFailureHasNoUntrustedCause','ssc301004IoFailureIdentityAnd50Remain','ssc301005UnknownRuntimeAndErrorRemainUnknown','ssc301006NullAndWrongSlotsRejectBeforeLoad','ssc301007NullResultDoesNotBecomeNormal70','ssc301008ConcurrentCallersNeverShareFailureSlot']
BATCH=['ssc302001ExactAuditAndIndependentArithmeticBoundaries','ssc302002StatusMustBeSuccess','ssc302003EndedMustMatchRetainedReference','ssc302004ExactSevenDayCutoffMustMatch','ssc302005BeforeNullIsNotZero','ssc302006AfterNullIsNotZero','ssc302007BeforeCannotBeBelowAfter','ssc302008BeforeMinusAfterMustEqualSuccess','ssc302009TargetMustEqualSuccess','ssc302010FailureCountMustBeZero','ssc302011SuccessfulAuditCannotCarryErrorCode','ssc302012SuccessfulAuditCannotCarryErrorSummary','ssc302013NullReferenceAndAuditAreContractViolations','ssc302014NonSkipAndNonzeroSelectedRejectBeforeAnyJdbc']
NEW_CASES=[('dev.codex.schubert.nk.api.bootstrap.ApiAdmittedConfigurationTest',name)for name in API]+[('dev.codex.schubert.nk.batch.file.RetainedExpiryAuditTest',name)for name in BATCH]


def physical_difference(old,new,candidate):
    import re
    if any(type(m)is not dict or any(type(k)is not str or type(v)is not str or re.fullmatch('[a-f0-9]{64}',v)is None for k,v in m.items())for m in [old,new,candidate]):raise ValueError('strict actual SHA256 inventories')
    if len(old)!=1646 or len(new)!=1647 or set(new)!=set(old)|INTERFACES or new!=candidate:raise ValueError('all1647 same-source inventory and one data-only interface required')
    changed={k for k in old if old[k]!=new[k]}
    if changed!=MODIFIED:raise ValueError('exact registered two implementation class deltas')
    values=[{'oldClass':k,'class':k,'oldSha256':old[k],'newSha256':new[k],'action':'MODIFIED'}for k in sorted(changed)]
    values.extend({'oldClass':None,'class':k,'oldSha256':None,'newSha256':new[k],'action':'ADDED_INTERNAL_INTERFACE'}for k in sorted(INTERFACES))
    return values,len(old)-len(changed)


def qualifier_source():
    raw=previous.qualifier_source()
    for old,new in [("out = base / 'runs/PG4694-six-v1'","out = base / 'runs/PG4844-six-v1'"),("source = base / 'source-full-PG4694'","source = base / 'source-full-PG4844'"),("old = base / 'runs/PG4420-six-v1'","old = base / 'runs/PG4694-six-v1'"),('transfer/PG4694-source.tar','transfer/PG4844-source.tar')]:
        if raw.count(old)!=1:raise ValueError('one genuine baseline/current path '+old)
        raw=raw.replace(old,new,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in {3721,3739,549,1646,18}:return ast.copy_location(ast.Constant({3721:3739,3739:3761,549:551,1646:1647,18:22}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    marker="    begin = json.loads((out / 'begin.safe.json').read_bytes())"
    extra="""
    format_proof=json.loads((out/'format-preflight.safe.json').read_bytes())
    order=json.loads((out/'format-before-pt.safe.json').read_bytes())
    need(format_proof['actualExit']==0 and format_proof['sameInputs']is True and format_proof['testsIssued']is False,'actual all-six format passed with unchanged inputs/no tests')
    need(format_proof['command'][-1:] == ['spotless:check'] and format_proof['command'][format_proof['command'].index('-pl')+1]==','.join('src/schubert-nk-'+m for m in ['protocol','storage','bootstrap','api','web','batch']),'exact all-six format only goals')
    need(order['allSixFormatBeforeAnyPt']is True and order['sourceInputsUnchanged']is True and order['formatProofSha256']==sha(out/'format-preflight.safe.json')and order['formatCompletedMtimeNs']<=order['ptStartEpochNs'],'durable all-six format precedes first PT command')
"""
    if raw.count(marker)!=1:raise ValueError('one immutable whole begin')
    raw=raw.replace(marker,marker+'\n'+extra,1)
    marker="need(path.stat().st_mtime >= start, 'fresh current XML')"
    if raw.count(marker)!=1:raise ValueError('one fresh XML boundary')
    raw=raw.replace(marker,marker+"\n                need(path.stat().st_mtime_ns>=order['ptStartEpochNs'],'all current XML after completed all-six format')")
    raw=raw.replace("'allSixMainBuildsPassed': True,","'allSixMainBuildsPassed': True, 'allSixFormatBeforeAnyPt':True, 'formatBeforePtProofSha256':sha(out/'format-before-pt.safe.json'),")
    return raw


def main():
    raw=inspect.getsource(previous.main)
    for old,new in [('pg4694-ssc299-six-v1','pg4844-ssc301-302-six-v1'),('pg4690-entry-termination-selected-v1','pg4848-expiry-host-tools-selected-v1'),('pg4428-shared-manager-whole-qualified-v1','pg4696-ssc299-whole-qualified-v1'),('PG4696-whole-qualified-v1','PG4846-whole-qualified-v1')]:raw=raw.replace(old,new)
    ns={**vars(previous),'SOURCE':SOURCE,'ROOT':ROOT,'W':W,'SLOT':SLOT,'MODIFIED':MODIFIED,'INTERFACES':INTERFACES,'NEW_CASES':NEW_CASES,'physical_difference':physical_difference,'qualifier_source':qualifier_source}
    exec(compile(raw,'<new3761 genuine XML and source qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
