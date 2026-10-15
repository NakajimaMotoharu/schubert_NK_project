"""Conservative current Java Files stream call-site inventory; no implicit ownership proof."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

CALL = re.compile(r'\bFiles\.(list|walk|find|lines)\s*\(')
OWNED = re.compile(r'\btry\s*\(\s*(?:var|Stream<[^>]+>)\s+\w+\s*=\s*(?:java\.nio\.file\.)?Files\.(list|walk|find|lines)\s*\(')


def inspect_text(text):
    result = []
    for line, content in enumerate(text.splitlines(), 1):
        for match in CALL.finditer(content):
            owned = OWNED.search(content)
            result.append({'line': line, 'operation': match.group(1),
                           'ownership': 'LEXICAL_TRY_RESOURCE' if owned and owned.end() == match.end() else 'MANUAL_REVIEW_REQUIRED'})
    return result


def main():
    root = Path(__file__).resolve().parents[2]
    result = []
    for path in sorted((root / 'src').rglob('*.java')):
        calls = inspect_text(path.read_text())
        for call in calls:
            result.append({'path': str(path.relative_to(root)), 'fileSha256': hashlib.sha256(path.read_bytes()).hexdigest(), **call})
    unknown = [r for r in result if r['ownership'] != 'LEXICAL_TRY_RESOURCE']
    value = {'actualExit': 1 if unknown else 0, 'productionSource': 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25',
             'assessmentHead': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
             'calls': result, 'count': len(result), 'manualReviewRequired': unknown,
             'scope': 'All src Java Files.list/walk/find/lines call sites; conservative one-line ownership admission; not a complete general Java resource analyzer',
             'runtimeProofRequired': 'BUG1289 before and after actual per-fixture procfs FD postcondition; full integration pending',
             'newPtCredit': 0, 'vmActions': 0, 'formalUpdated': False}
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return value['actualExit']


if __name__ == '__main__':
    raise SystemExit(main())
