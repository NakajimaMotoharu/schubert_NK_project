"""One explicit immutable stage, read-only inspect, then separate unused placement."""
import json
import sys
from pyflakes.api import check
import pg3986_literal_invariant_unused_dispatch as previous
import pg4454_inspectable_failed_unused_sources as role
from pg4434_current_candidate_admission_read import authenticate_host
from pg1674_critical_management_gate import management_gate
from pg1446_current_cold_stage import P

TARGET = role.W / role.TOOLS
GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
DESIGN_MAIN = 'd2a940313447ec0c63168f3332a9835753586b9c'


def bind(raw):
    return role.role_text(role.previous.role_text(raw))


def stage_source():
    return bind(previous.stage_source()).replace('/home/ubuntu/pg4448-fixed-stage-v1/', '/home/ubuntu/pg4462-fixed-stage-v1/')


def stage_qualified(value):
    expected = {'actualExit':0,'payloadSha256':'aef4fcbdd91c2193e8db3dfb95dbfa252f3043aa5fd155255402dcbdc5e39614',
        'frozenFiles':142,'originalStageActualExit':1,'originalStageReplayed':False,'filesRetransferred':False,
        'candidateSource':role.SOURCE,'currentSource':role.CURRENT,'guestTools':GUEST,'candidatePlaced':False,'formalAccepted':False}
    return type(value) is dict and all(type(value.get(k)) is type(v) and value[k] == v for k,v in expected.items())


def source():
    raw = bind(previous.source())
    once = role.previous.once
    raw = once(raw, "(['stage'],['place'])", "(['stage'],['inspect'],['place'])")
    raw = once(raw, "W/'pg4446-frozen-v1.safe.json'", "W/'pg4460-frozen-v1.safe.json'")
    raw = once(raw, "W/'pg3980-current-before-view-v1/manifest.safe.json'", "W/'pg4442-failed-current-view-qualified-v1/manifest.safe.json'")
    raw = raw.replace("frozen['genuineParentBeforeSha256']", "frozen['failedCurrentDataBeforeSha256']")
    raw = once(raw, "if frozen['actualExit']!=0 or current['actualExit']!=0", "if frozen['actualExit']!=0 or frozen['completeGraphQualified']is not True or current['actualExit']!=0")
    raw = raw.replace("current['productionSource']", "current['source']")
    raw = raw.replace('pg4448-', 'pg4462-')
    # Restore fixed archive/input/tool identities; observer namespaces alone are
    # PG4462. The file names in the closed18 artifact are not regenerated here.
    raw = raw.replace('pg4462-shared-manager-release-v4.tar', role.ARCHIVE)
    raw = raw.replace('pg4462-shared-manager-input-v4', 'pg4448-shared-manager-input-v4')
    raw = once(raw, "'Pg4444UnusedStage place'", "'Pg4444UnusedStage '+action")
    raw = once(raw, "if(W/'pg4462-stage-v1.exit').read_bytes()!=b'0\\n':raise ValueError('actual immutable tool/input stage required')",
        "if not stage_qualified(json.loads((W/'pg4468-existing-input-stage-v1/manifest.safe.json').read_bytes())):raise ValueError('actual same142 existing-input consumer required; original stage1 preserved')")
    marker = "    action=sys.argv[1];frozen="
    raw = once(raw, marker, "    action=sys.argv[1]\n    if action=='place' and (W/'pg4462-inspect-v1.exit').read_bytes()!=b'0\\n':raise ValueError('genuine same-artifact inspect0 required before placement')\n    frozen=")
    compile(raw, '<new explicit failed-current unused operator>', 'exec')
    return raw


def runtime_namespace(candidate):
    facts = role.previous.proof(); role.candidate_bom()
    role.previous.require(facts['oldParentNormal'] is False and facts['runtimeAuthorityIssued'] is False
        and facts['newScopesNormal'] is True and facts['canonicalBefore10Sha256'] == role.BEFORE)
    engine = previous.previous.previous.old.previous.engine
    namespace = {**engine.base.__dict__, '__file__':__file__, 'TARGET':TARGET, 'GUEST':GUEST, 'REMOTE':role.REMOTE,
        'STAGE':stage_source(), 'SOURCE':role.SOURCE, 'DIGEST':candidate['manifestSha256'],
        'BASELINE_SHA':role.BEFORE, 'sources':role.sources, 'stage_qualified':stage_qualified}
    role.previous.require(candidate['actualExit'] == 0 and candidate['candidateSource'] == role.SOURCE
        and candidate['manifestSha256'] == role.BOM and candidate['signatureVerified'] is True)
    return namespace


def main():
    if sys.argv[1:] not in [['stage'],['inspect'],['place']]: raise ValueError('one explicit finite action')
    if DESIGN_MAIN == 'PENDING_SSC296_MAIN': raise ValueError('final design-only main publication required first')
    import subprocess
    subprocess.run(['git','merge-base','--is-ancestor',DESIGN_MAIN,'origin/main'],check=True)
    role.qualify(); authenticate_host()
    candidate = json.loads((role.W/'pg4432-candidate-build-v1.safe.json').read_bytes())
    namespace = runtime_namespace(candidate); raw = source()
    if 'management_gate' in raw: raise ValueError('do not nest management gates')
    # main receives its explicitly constructed known engine namespace; the stage
    # payload is standalone and receives the complete immutable file dictionary.
    if check("DIGEST='fixed-stage-digest'\nFILES={}\n" + stage_source(), '<complete immutable guest stage>'): raise ValueError('all stage static0')
    exec(compile(raw, '<same-artifact stage/inspect/place>', 'exec'), namespace)
    with management_gate(P/'current-management-critical.lock'):
        return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
