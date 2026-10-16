"""This fresh cohort's unchanged terminal/SQL/seal oracles, explicit actual snapshot view."""
import inspect
import json
import sys
import types
import pg4022_literal_invariant_acceptance as previous
import pg2079_current_same_day_rows_capture as row_template
import pg4250_current_admission_image as admission
from pg4060_original_profile_dual_stack import once
from pg1446_current_cold_stage import W

TERM='pg4252-current-genuine-terminal-v1'
ROWS='pg4254-current-all24-rows-v1'
SEAL='pg4256-current-whole-seal-v1'


def bind(raw):
    for old,new in [('pg4016-literal-invariant-current-noargs-once-v1',admission.ONCE),
                    ('pg4018-literal-invariant-current-live-binding-v1',admission.LIVE),
                    ('pg4012-parent-watch-v1','pg4220-parent-watch-v1'),
                    (previous.TERM,TERM),(previous.ROWS,ROWS),(previous.SEAL,SEAL)]:raw=raw.replace(old,new)
    return raw


def terminal_payload(binding):return bind(previous.terminal_payload(binding))


def rows_payload(binding,before_hash):
    raw=inspect.getsource(row_template.payload)
    for old,new in [('pg2074-current-newrun-live-binding-v1',admission.LIVE),
                    ('pg2072-current-noargs-newrun-once-v1',admission.ONCE),
                    ('796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05',before_hash),
                    ('pg2079-current-same-day-rows-capture-v1',ROWS),
                    ('3d69f5af-6bac-46b1-a540-7591c4a79a0d','79a3260a-e16d-42bf-942a-b914ed144c28')]:raw=raw.replace(old,new)
    raw=once(raw,"binding=actual['binding']","binding=actual['result']['binding']")
    raw=once(raw,"actual['productionSource']","actual['source']")
    ns={**vars(row_template),'transport':types.SimpleNamespace(SOURCE=admission.SOURCE)}
    exec(compile(raw,'<actual current rows factory>','exec'),ns);result=ns['payload']()
    result=once(result,"before=json.loads(br)","before=json.loads(br);before={'rows':before['database']['rows']}")
    marker='sql="begin isolation level repeatable read read only;'
    guard="manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json');original_manifest=manifest.read_bytes();require(hashlib.sha256(original_manifest).hexdigest()==BOM and json.loads(original_manifest)['source']['commit']==SOURCE)\n"
    result=once(result,marker,guard+marker)
    result=once(result,"print(json.dumps({**result,'actualExit':0,","require(manifest.read_bytes()==original_manifest)\nprint(json.dumps({**result,'actualExit':0,")
    return 'SOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+'\n'+result


def seal_payload(binding,before_hash):
    ns=previous.namespace()
    fn=types.FunctionType(ns['seal_payload'].__code__,{**ns,'before':lambda:before_hash})
    raw=bind(fn(binding))
    start=raw.index('def before_shape(before):')
    end=raw.index('\nOWNED={}',start)
    # Only map recorded observation fields. The signed publication supplies static
    # Unit bytes, never historical PID1, live rows, native observations or outcomes.
    view=inspect.getsource(admission.project)+'\n'
    view+="publication_raw=(BASE/'pg4008-literal-invariant-publication-independent-post-v1/after.private.json').read_bytes();require(hashlib.sha256(publication_raw).hexdigest()=="+repr(admission.PUBLICATION)+")\n"
    view+="before=project(before,json.loads(publication_raw))\nold['unitFilesActual']=before['unitFilesActual']\n"
    return raw[:start]+view+raw[end:]


def payload(phase):
    b=admission.live();h=admission.before()
    if phase=='terminal':return TERM,terminal_payload(b)
    if phase=='rows':return ROWS,rows_payload(b,h)
    if phase=='seal':return SEAL,seal_payload(b,h)
    raise ValueError('terminal/rows/seal only')


def main(phase):
    if phase in {'rows','seal'}:
        term=json.loads((W/TERM/'manifest.safe.json').read_bytes())
        if term['actualExit']!=0 or term['source']!=admission.SOURCE or term['result']['genuineRootDone']is not True:raise ValueError('actual same-cohort genuine terminal required')
    if phase=='seal':
        rows=json.loads((W/ROWS/'manifest.safe.json').read_bytes())
        if rows['actualExit']!=0 or rows['source']!=admission.SOURCE:raise ValueError('actual same-source all24 required')
    slot,raw=payload(phase);return admission.execute(slot,raw,90)


if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
