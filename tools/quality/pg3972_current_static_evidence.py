"""Public hash/count receipts only, no private logs, key, native or session export."""
import hashlib
import json
from pg3966_literal_invariant_full_six import ROOT, W, SOURCE, require


def main():
    path = W / 'pg3970-current-main-static-v1/manifest.safe.json'; value = json.loads(path.read_bytes()); r = value['result']
    require(value['actualExit'] == 0 and value['productionSource'] == r['mainGitSource'] == SOURCE and r['sourceFiles'] == 849 and r['pmd']['processingErrors'] == 0, 'actual pinned current-source diagnostic')
    require(r['pmd']['actualExit'] == 4 and r['pmd']['rawFindings'] == 1653 and r['checkstyle']['actualExit'] == r['checkstyle']['findings'] == 0 and not r['F03Accepted'], 'raw diagnostics are not a zero-violation gate')
    readonly_path = W / 'pg3978-current-preservation-readonly-v1/manifest.safe.json'; readonly = json.loads(readonly_path.read_bytes())
    require(readonly['actualExit'] == 0 and readonly['result']['native46Preserved'] and readonly['result']['guestFilesWritten'] == 0, 'actual no-action preserved current VM read')
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3972-current-static-readonly-v1'; out.mkdir()
    objects = {'all-849-main-sha256.json': r['allMainSha256'], 'fixed-static-receipt.json': {k: v for k, v in r.items() if k != 'allMainSha256'}, 'preservation-readonly-receipt.json': readonly}
    for name, obj in objects.items(): (out / name).write_text(json.dumps(obj, sort_keys=True, indent=2) + '\n')
    manifest = {'actualExit': 0, 'productionSource': SOURCE, 'sourceSnapshot': r['sourceSnapshot'], 'testIds': ['PT-F03-STATIC-3970', 'PT-OPS-RO-3978'],
                'command': 'pg3970_current_main_static.py; pg3978_current_preservation_readonly.py', 'branch': 'dev-foundation', 'os': 'Linux aru host/PGPT isolated guest',
                'jdk': '25.0.4', 'pmd': '7.28.0 existing qualified record overlay', 'checkstyle': '14.3.0',
                'pmdActualExit': 4, 'pmdRawFindings': 1653, 'pmdProcessingErrors': 0, 'checkstyleActualExit': 0, 'checkstyleFindings': 0,
                'suppressionAdded': False, 'rulesChanged': False, 'applicableViolationCount': None, 'technicalDispositionsCurrentSource': None,
                'F03Accepted': False, 'formalAccepted': False, 'formalTests': 1964, 'formalScopes': 53, 'effortPercent': None,
                'currentSourceNativeImported': False, 'qa051Final': 'HELD', 'vmWrites': 0, 'vmStarts': 0,
                'staticServerManifestSha256': r['serverManifestSha256'], 'staticLocalReceiptSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'readonlyLocalReceiptSha256': hashlib.sha256(readonly_path.read_bytes()).hexdigest(),
                'relatedBug': ['BUG1330', 'YKT1096'], 'files': {n: hashlib.sha256((out / n).read_bytes()).hexdigest() for n in objects}}
    (out / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest(), 'F03Accepted': False}))
    return 0


if __name__ == '__main__': raise SystemExit(main())
