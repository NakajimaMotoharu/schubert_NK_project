"""Current observed a2ecc existingADMIN20 graph; historical constructors confer no permission."""
import inspect
import json
import types
import pg4932_current_bootstrap_sources as previous
import pg5080_current_bootstrap_before as before
import pg5060_current_owned_sources as owned

SOURCE, BOM, W = before.SOURCE, before.BOM, before.admission.W
TOOLS = 'pg5082-current-bootstrap-tools-v1'
BASELINE = 'af59c9ebb4bac4bac238f81ae28cb5bf2840b6e32ee529b2ec7ee514054faa1e'


def current_text(raw):
    fn = types.FunctionType(previous.current_text.__code__,
                            {**vars(previous), 'SOURCE': SOURCE, 'BOM': BOM, 'TOOLS': TOOLS, 'before': before})
    raw = fn(raw)
    pairs = [('Pg4932', 'Pg5082'), ('PG4932', 'PG5082'), ('pg4932', 'pg5082'),
             ('PG4860', 'PG4980'), ('pg4860', 'pg4980'),
             ('4e220f3b-fbb4-411c-b5c4-7ca1371daa20', '15322936-6512-4550-8123-a3ef688dc1da'),
             ('2026-10-17T01:03:09.221494Z', '2026-10-18T07:15:03.563840Z'),
             ('7bae6042-b79f-4fb2-9d9f-edf47b428cbe', 'b683da46-df42-4e52-8379-5ac8bfbca0ae'),
             ('2026-10-17T01:29:28.803598Z', '2026-10-18T07:40:43.315378Z'),
             ('7fe303d625de4a83b23d23fca4eca2bb', 'abe95f4c09b849a8a2304e94a3cb8165'),
             ('199849150395', '306951851178'), ('pg4916', 'pg5060'), ('==884', '==894')]
    for old, new in pairs:
        raw = raw.replace(old, new)
    return raw


def eligibility(baseline_sha):
    outer = json.loads((W / before.SLOT / 'manifest.safe.json').read_bytes())
    result = outer['result']
    if not (type(outer['actualExit']) is int and outer['actualExit'] == 0 and outer['source'] == SOURCE
            and result['productionSource'] == SOURCE and type(result['actualExit']) is int and result['actualExit'] == 0
            and result['beforeSha256'] == baseline_sha == BASELINE and result['batchRows'] == 894
            and result['nativePhysicalFiles'] == 86 and all(result[k] is True for k in
                ('whole24Full32Signed187AndResourcesUnchanged', 'existingSingleAdminVerified',
                 'bootstrapCredentialsAbsent', 'emptyFourNamespacesVerified', 'normalNewReferences', 'startsStopsWrites0'))):
        raise ValueError('actual5080 exact stopped a2ecc baseline required')
    return result


def files(baseline_sha):
    raw = inspect.getsource(previous.files)
    for old, new in [('Pg4932', 'Pg5082'), ('PG4932', 'PG5082'), ('pg4932', 'pg5082'),
                     ('pg4916_parent_receipt.py', 'pg5060_parent_receipt.py')]:
        raw = raw.replace(old, new)
    ns = {**vars(previous), 'SOURCE': SOURCE, 'BOM': BOM, 'W': W, 'TOOLS': TOOLS, 'BASELINE': BASELINE,
          'before': before, 'owned': owned, 'eligibility': eligibility, 'current_text': current_text}
    exec(compile(raw, '<current observed894/86 existing20 graph>', 'exec'), ns)
    return ns['files'](baseline_sha)
