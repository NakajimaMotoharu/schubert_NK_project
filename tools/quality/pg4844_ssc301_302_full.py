"""One required frozen full campaign for combined SSC301/302; actual all-six format first."""
import ast
import inspect
import json
import pg4694_ssc299_full as previous

SOURCE='04bbdb73b532537e3546191d72dee913b17629a0'
LABEL='PG4844'
ROOT,W=previous.ROOT,previous.W


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG4694',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in {3739,549,1646}:return ast.copy_location(ast.Constant({3739:3761,549:551,1646:1647}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    # Durable time/order receipts supplement, not replace, the original exact format prerequisite.
    marker='    format_preflight(args, SOURCE, OUT, env, inputs)'
    if raw.count(marker)!=1:raise ValueError('one exact all-six format before any PT')
    addition="""
    format_proof=json.loads((OUT/'format-preflight.safe.json').read_bytes())
    assert format_proof['actualExit']==0 and format_proof['sameInputs']is True and format_proof['testsIssued']is False
    format_stat=(OUT/'format-preflight.safe.json').stat()
    pt_start_ns=__import__('time').time_ns()
    assert format_stat.st_mtime_ns<=pt_start_ns
    with(OUT/'format-before-pt.safe.json').open('x')as f:
        json.dump({'allSixFormatBeforeAnyPt':True,'formatProofSha256':sha(OUT/'format-preflight.safe.json'),'formatCompletedMtimeNs':format_stat.st_mtime_ns,'ptStartEpochNs':pt_start_ns,'sourceInputsUnchanged':all(sha(SOURCE/p)==h for p,h in inputs.items())},f,sort_keys=True);f.flush();os.fsync(f.fileno())
"""
    raw=raw.replace(marker,marker+'\n'+addition,1)
    compile(raw,'<one whole3761/551/all1647 all-six format first>','exec');return raw


def main():
    selected=json.loads((W/'pg4848-expiry-host-tools-selected-v1/manifest.safe.json').read_bytes())
    if not(selected['actualExit']==selected['actualMavenExit']==0 and selected['sourceSnapshot']==SOURCE and selected['suites']==10 and selected['tests']==59):raise ValueError('actual combined59 ten-suite helpers/original DB first')
    if set(selected['coverage'])!={'api.admittedConfiguration','batch.verifyPriorAudit','batch.verifyPriorExpiry'}or any(v.get(k,{'missed':0})['missed']!=0 for v in selected['coverage'].values()for k in ('LINE','METHOD','BRANCH')):raise ValueError('three actual methods all conditions first')
    raw=inspect.getsource(previous.previous.main)
    raw=raw.replace('pg4420','pg4844').replace('shared-manager','ssc301-302')
    raw=raw.replace("'tests': 3721, 'suites': 545, 'mainClasses': 1644","'tests': 3761, 'suites': 551, 'mainClasses': 1647")
    raw=raw.replace('SSC295 shared strict native manager reader across bootstrap/batch; old7bb native not portable; selected4412 NoTests preserved','SSC301 admitted API config and SSC302 retained audit predicates, independent22 new PT; combined selected4842; old825e native not portable; all-six format preflight required; no unnecessary old whole replay')
    ns={**vars(previous.previous),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(raw,'<combined required whole once>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
