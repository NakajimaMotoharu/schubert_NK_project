"""Read-only correction proof against immutable pre-edit blobs; new-only public evidence."""
import hashlib
import json
import subprocess
from collections import defaultdict
from pg5940_private_lock_compile import ROOT, BASE, sha
from pg6580_api_mapper_plan import SOURCE, transform, semantic_hash


def verify():
    original = BASE/'PG6580-api-mapper-plan-v1/plan.json'
    plan = json.loads(original.read_bytes())
    inventory = BASE/'PG6542-jdbc-catch-inventory-v1'
    if sha(inventory/'manifest.json') != 'd8aa3acc4f287da8581fdbdf5c2a25ce8ae94b15c468fd02acae35c043ef4435':
        raise ValueError('immutable113 inventory')
    if sha(inventory/'sites.json') != json.loads((inventory/'manifest.json').read_bytes())['inventorySha256']:
        raise ValueError('immutable113 rows')
    groups = defaultdict(list)
    for row in json.loads((inventory/'sites.json').read_bytes()):
        groups[row['sourcePath']].append(row['siteId'])
    rows = []
    for row in plan['files']:
        path = row['path']
        old = subprocess.check_output(['git', 'show', SOURCE+':'+path], cwd=ROOT)
        if hashlib.sha256(old).hexdigest() != row['oldSha256']:
            raise ValueError('original per-file source identity')
        expected, actions, exclusions = transform((ROOT/path).stem, old.decode(), groups[path])
        actual = (ROOT/path).read_text()
        if semantic_hash(actual) != semantic_hash(expected):
            raise ValueError('unplanned body/literal/import change: '+path)
        rows.append(dict(path=path, oldSha256=row['oldSha256'], actualSha256=sha(ROOT/path),
                         semanticV2Sha256=semantic_hash(expected), actions=len(actions), exclusions=len(exclusions)))
    changed = set(subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=ROOT,text=True).splitlines())
    if len(rows) != 19 or changed != {r['path'] for r in rows} | {
            'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionProviderFailureGraph329Test.java'}:
        raise ValueError('exact19 Main and declared provider Test only')
    if subprocess.check_output(['git','diff','d925f25cf8c55a4fa70ecb61ac334fdb9802c77b','--',':(glob)src/*/src/test/**'],cwd=ROOT):
        raise ValueError('all original red/old Test bytes fixed')
    return dict(status='PG_CORRECTION_CHECKED_PT_PENDING', sourceBaseline=SOURCE,
                head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                bug='BUG-1594', horizontal='YKT-1347', originalPlanSha256=sha(original),
                semanticAlgorithm='V2_SORTED_IMPORT_TOKEN_MULTISET_AND_ORDERED_BODY_LITERAL_TOKENS',
                originalV1PlanRewritten=False, files=rows,
                correctedImportHeaders=['JdbcInboxCoordinator','WebLogIngestService','InboxCleanup'],
                otherImportHeadersChecked=16, productionPtPassAdded=0, formalChanged=False)


def main():
    value=verify(); path=BASE/'PG6580-api-mapper-plan-v1/correction-v2.json'
    with path.open('x') as output:
        output.write(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(path=str(path),sha256=sha(path),files=len(value['files']),actualExit=0)))


if __name__=='__main__':main()
