"""SSC303 current existing20 graph; current observations, never old success authority."""
import inspect
import json
import types
import pg4820_new_current_bootstrap_sources as previous
import pg4930_current_bootstrap_before as before
import pg4916_current_owned_sources as owned

SOURCE,BOM,W=before.SOURCE,before.BOM,before.admission.W
TOOLS='pg4932-current-bootstrap-tools-v1'
BASELINE='28c6679e2bd13f84e33c21ea9dbcb2a5baa1e8efda7b2780471f80e74a6f6a63'


def current_text(raw):
    raw=types.FunctionType(previous.current_text.__code__,{**vars(previous),'SOURCE':SOURCE,'BOM':BOM,'TOOLS':TOOLS,'before':before})(raw)
    pairs=[('Pg4820','Pg4932'),('PG4820','PG4932'),('pg4820','pg4932'),
           ('PG4702','PG4860'),('pg4702','pg4860'),
           ('fff841d9-2554-4680-b17d-9548bfa79cbb','4e220f3b-fbb4-411c-b5c4-7ca1371daa20'),
           ('2026-10-16T22:12:38.570783Z','2026-10-17T01:03:09.221494Z'),
           ('7ab6c953-b2fc-47ae-be96-26a3196ca76d','7bae6042-b79f-4fb2-9d9f-edf47b428cbe'),
           ('2026-10-16T22:39:38.673291Z','2026-10-17T01:29:28.803598Z'),
           ('b414b0e1e5ac47e8b5fb8c5ae3d94348','7fe303d625de4a83b23d23fca4eca2bb'),
           ('189659374308','199849150395'),('pg4772','pg4916'),('==874','==884')]
    for old,new in pairs:raw=raw.replace(old,new)
    return raw


def eligibility(baseline_sha):
    value=json.loads((W/before.SLOT/'manifest.safe.json').read_bytes());result=value['result']
    if not(type(value['actualExit'])is int and value['actualExit']==0 and value['source']==SOURCE
           and result['productionSource']==SOURCE and type(result['actualExit'])is int and result['actualExit']==0
           and result['beforeSha256']==baseline_sha==BASELINE and result['batchRows']==884
           and result['nativePhysicalFiles']==78 and all(result[k]is True for k in
           ('whole24Full32Signed187AndResourcesUnchanged','existingSingleAdminVerified',
            'bootstrapCredentialsAbsent','emptyFourNamespacesVerified','normalNewReferences','startsStopsWrites0'))):
        raise ValueError('actual4930 current full baseline required; old success cannot authorize')
    return result


def files(baseline_sha):
    raw=inspect.getsource(previous.files)
    for old,new in [('Pg4820','Pg4932'),('PG4820','PG4932'),('pg4820','pg4932'),
                    ('pg4772_parent_receipt.py','pg4916_parent_receipt.py'),
                    ('pg4772-new-current-owned-tools-v1',owned.TOOLS)]:raw=raw.replace(old,new)
    ns={**vars(previous),'SOURCE':SOURCE,'BOM':BOM,'W':W,'TOOLS':TOOLS,'BASELINE':BASELINE,
        'before':before,'eligibility':eligibility,'current_text':current_text}
    exec(compile(raw,'<current same-authority existing20 graph>','exec'),ns)
    return ns['files'](baseline_sha)
