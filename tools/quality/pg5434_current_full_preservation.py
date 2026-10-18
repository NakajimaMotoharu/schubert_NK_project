"""Fresh current A2 full11/all24/originals/native88 read; old authority never transferred."""
import ast
import hashlib
import json
from pyflakes.api import check
import pg5108_corrected_bootstrap_post as previous
import pg5036_current_admission_image as admission
from pg5432_current_vm_reauthentication import SLOT as INITIAL,CURRENT,CURRENT_BOM,CANDIDATE

W=admission.W
SLOT='pg5434-current-full-preservation-v1'


def payload():
    original=W/previous.SLOT/'manifest.safe.json';receipt=json.loads(original.read_bytes())
    raw=previous.payload()
    if receipt['actualExit']!=0 or receipt['source']!=CURRENT or hashlib.sha256(raw.encode()).hexdigest()!=receipt['payloadSha256']:
        raise ValueError('exact original independent closed A2 post reader, not a reconstructed oracle')
    marker='save = base / '+repr(previous.SLOT)
    if raw.count(marker)!=1:raise ValueError('one new evidence output target only')
    raw=raw.replace(marker,'save = base / '+repr(SLOT),1)
    tree=ast.parse(raw)
    # The original SQL snapshot explicitly enforces a read-only repeatable-read transaction.
    queries=[node for node in ast.walk(tree) if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='q' for target in node.targets)]
    if len(queries)!=1 or not isinstance(queries[0].value,ast.Constant) or 'repeatable read read only' not in queries[0].value.value:
        raise ValueError('original database capture must remain transaction-read-only')
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ('unlink','rename','replace','rmdir','write_text','write_bytes'):
            raise ValueError('no business/runtime/file mutation fallback in fresh read')
    if check(raw,'<new output only fresh A2 full preservation>'):raise ValueError('complete standalone static0')
    compile(raw,'<fresh current full11, no same-source candidate native claim>','exec')
    return raw


def main():
    initial=json.loads((W/INITIAL/'manifest.safe.json').read_bytes())
    if initial['actualExit']!=0 or initial['source']!=CURRENT or initial['candidateSource']!=CANDIDATE or (
        initial['result']['bomSha256']!=CURRENT_BOM or initial['result']['artifactsVerified']!=187 or initial['result']['signatureVerifyExit']!=0):
        raise ValueError('actual current existing guest reauthentication first')
    return admission.execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
