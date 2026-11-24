"""Public numbered-evidence follow-up index; candidate lookup, never acceptance or permission."""
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from host_tool_invocation import capture, verify
from verify_published_manifest_pins import SHA256, exact_source, git

ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'evidence/01_PT/018_NK-OPS-001'
OUT=DOCS/'evidence/provisional/PG8150-evidence-followup-guard-v1'
NAME=re.compile(r'([0-9]{3,4})_[^/\\]+\.md')


def query_value(query):
    if not isinstance(query,str) or not query.strip() or len(query)>128 or any(ord(c)<32 for c in query):
        raise ValueError('bounded nonempty public evidence literal required')
    return query.casefold()


def eligible(name):
    return isinstance(name,str) and NAME.fullmatch(name) is not None and '.private.' not in name.casefold()


def index_entries(query,entries):
    needle=query_value(query)
    rows=[]
    for name,body in entries:
        if not eligible(name):
            continue
        if not isinstance(body,str):
            raise ValueError('public UTF8 evidence body required')
        if needle not in (name+'\n'+body).casefold():
            continue
        number=int(NAME.fullmatch(name).group(1))
        title=body.splitlines()[0] if body.splitlines() else ''
        rows.append(dict(number=number,name=name,title=title,sha256=hashlib.sha256(body.encode()).hexdigest()))
    return sorted(rows,key=lambda row:(-row['number'],row['name']))


def corpus():
    result=[]
    for file in DOCS.iterdir():
        if not eligible(file.name):
            continue
        if file.is_symlink() or not file.is_file() or file.stat().st_size>1024*1024:
            raise ValueError('only bounded regular public numbered evidence files')
        result.append((file.name,file.read_text()))
    return result


def public_manifest_path(path):
    parts = PurePosixPath(path).parts
    return (
        parts[:2] == ("evidence", "01_PT")
        and len(parts) in (6, 7)
        and parts[3] == "evidence"
        and (len(parts) == 6 or parts[4] == "provisional")
        and re.fullmatch(r"(?i)PG[0-9]+(?:[-_].+)?", parts[-2]) is not None
        and "private" not in parts[-2].casefold()
        and parts[-1] == "manifest.json"
    )


def digest_candidates(repo, source, digests):
    if not exact_source(source) or not 1 <= len(digests) <= 8:
        raise ValueError("a full Git commit and one to eight SHA-256 digests are required")
    if any(not isinstance(value, str) or not SHA256.fullmatch(value) for value in digests):
        raise ValueError("expected lowercase SHA-256 digests")
    commit = git(repo, "rev-parse", "--verify", "--end-of-options", f"{source}^{{commit}}")
    if commit.stdout.decode().strip() != source:
        raise ValueError("source must be a Git commit")

    tree = git(repo, "ls-tree", "-r", "-z", source, "--", "evidence/01_PT").stdout
    manifests = []
    for row in tree.decode("utf-8").split("\0"):
        metadata, _, path = row.partition("\t")
        if metadata.startswith(("100644 blob ", "100755 blob ")) and public_manifest_path(path):
            manifests.append(path)

    query = ["grep", "-I", "-F", "-l", "-z", "--all-match", "--no-textconv"]
    distinct = sorted(set(digests))
    for value in distinct:
        query.extend(("-e", value))
    patterns = [
        re.compile(rb"(?<![0-9A-Fa-f])" + value.encode("ascii") + rb"(?![0-9A-Fa-f])")
        for value in distinct
    ]

    candidates = set()
    for start in range(0, len(manifests), 500):
        selected = manifests[start : start + 500]
        result = git(repo, *query, source, "--", *selected, required=False)
        if result.returncode == 1:
            continue
        result.check_returncode()
        for row in result.stdout.decode("utf-8").split("\0"):
            if not row:
                continue
            prefix, sep, path = row.partition(":")
            if prefix != source or not sep or path not in selected:
                raise ValueError("unexpected Git manifest match")
            blob = git(repo, "cat-file", "blob", f"{source}:{path}").stdout
            if all(pattern.search(blob) is not None for pattern in patterns):
                candidates.add(path)

    return {
        "source": source,
        "digests": distinct,
        "trackedPublicManifests": len(manifests),
        "paths": sorted(candidates),
        "acceptanceInferred": False,
    }


class FollowupTest(unittest.TestCase):
    def test_FOLLOWUP001_number_order_not_modification_or_acceptance(self):
        rows=index_entries('C02',[('1520_old.md','# C02 old gap'),('1555_result.md','# C02 result'),
                                   ('1733_repeat.md','# C02 repeat'),('1553_spec.md','# C02 spec')])
        self.assertEqual([1733,1555,1553,1520],[r['number'] for r in rows])
        self.assertTrue(all(set(r)=={'number','name','title','sha256'} for r in rows))
        self.assertEqual('1555_result.md',rows[1]['name'])

    def test_FOLLOWUP002_literal_unicode_and_case(self):
        entries=[('1734_索引.md','# C02 contract.* [literal]'),('1557_result.md','# C06')]
        self.assertEqual(['1734_索引.md'],[r['name'] for r in index_entries('c02',entries)])
        self.assertEqual(['1734_索引.md'],[r['name'] for r in index_entries('.*',entries)])
        self.assertEqual([],index_entries('C0[26]',entries))
        self.assertEqual([],index_entries('missing',entries))
        self.assertEqual('# C02 contract.* [literal]',index_entries('c02',entries)[0]['title'])

    def test_FOLLOWUP003_invalid_query_and_metadata(self):
        for value in (None,False,0,'','  ','x'*129,'C02\n','C02\x00'):
            with self.assertRaises(ValueError):
                index_entries(value,[])
        with self.assertRaises(ValueError):
            index_entries('C02',[('1734_public.md',None)])

    def test_FOLLOWUP004_private_and_path_scope_not_authority(self):
        entries=[('1734_public.md','# C02'),('1734_public.private.md','# C02'),
                 ('../../1734_public.md','# C02'),('private/1734_public.md','# C02'),
                 ('untracked.md','# C02'),('17340_public.md','# C02')]
        rows=index_entries('C02',entries)
        self.assertEqual(['1734_public.md'],[r['name'] for r in rows])
        self.assertFalse(any('accepted' in key.lower() or 'allowed' in key.lower() for row in rows for key in row))


class DigestCandidatesTest(unittest.TestCase):
    def test_uses_exact_digests_together_in_tracked_git_manifests(self):
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            git(repo, "init", "-q")
            prefix = "evidence/01_PT/001_PROGRAM/evidence/"
            first = "a" * 64
            second = "b" * 64
            both = json.dumps({"product": first, "fixture": second}, indent=2)
            good = prefix + "PG01-pure-result/manifest.json"
            provisional = prefix + "provisional/PG02-pure-result/manifest.json"
            entries = {
                good: both,
                provisional: both,
                prefix + "PG03-other/manifest.json": json.dumps([first]),
                prefix + "PG04-other/manifest.json": json.dumps([second]),
                prefix + "PG05-near-match/manifest.json": json.dumps([first + "a", second]),
                prefix + "PG06-private/manifest.json": both,
                prefix + "raw/PG07-result/manifest.json": both,
                prefix + "PG08-result/raw.json": both,
            }
            for path, content in entries.items():
                file = repo / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(content, encoding="utf-8")
            symlink = repo / (prefix + "PG09-link/manifest.json")
            symlink.parent.mkdir()
            symlink.symlink_to(repo / good)
            git(repo, "add", "--", "evidence/01_PT")
            git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "-qm", "fixture")
            source = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
            (repo / good).write_text("dirty replacement", encoding="utf-8")
            untracked = repo / (prefix + "PG10-untracked/manifest.json")
            untracked.parent.mkdir()
            untracked.write_text(both, encoding="utf-8")

            results = digest_candidates(repo, source, [first, second])

            self.assertEqual([good, provisional], results["paths"])
            self.assertEqual(5, results["trackedPublicManifests"])
            self.assertFalse(results["acceptanceInferred"])
            self.assertEqual([], digest_candidates(repo, source, ["c" * 64])["paths"])

    def test_validates_inputs_before_accessing_git(self):
        for source, digests in (("HEAD", ["a" * 64]), ("a" * 40, []),
                                ("a" * 40, ["a" * 63]), ("a" * 40, ["x" * 64] * 9)):
            with self.subTest(source=source, digests=digests), self.assertRaises(ValueError):
                digest_candidates(Path("nonexistent-repository"), source, digests)


def qualify():
    invocation=capture(Path(__file__))
    if OUT.exists():
        raise ValueError('new-only follow-up guard evidence, no replay')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FollowupTest))
    entries=corpus()
    snapshots={}
    for query,required in (
        ('C02','1555_C02四設定_実行結果.md'),
        ('C06','1557_C06_Batch既定値・非秘密設定境界_実行結果.md'),
        ('WebDbPool','1728_WebPool観測結線_単体テスト仕様書.md'),
        ('Prometheus','1730_Prometheus配布設定_単体テスト仕様書.md')):
        rows=index_entries(query,entries)
        prior=[row for row in rows if row['name']==required]
        if len(prior)!=1:
            raise ValueError('required actual prior follow-up must be visible before selecting next work')
        snapshots[query]=dict(matches=len(rows),newest=rows[:10],mandatoryPrior=prior[0],
                              acceptanceInferred=False,readPriorBodyBeforeSelectingNext=True)
    witnesses={}
    for name in ('PG7036-c02-four-template-host-v1','PG7038-c02-four-template-post-v1',
                 'PG7040-c06-config-template-host-v1','PG7042-c06-config-template-post-v1',
                 'PG8134-web-pool-qualification-v1','PG8140-prometheus-config-pt-v1',
                 'PG8146-c02-four-profiles-pt-v1'):
        file=DOCS/'evidence/provisional'/name/'manifest.json'
        item=json.loads(file.read_bytes())
        if item['actualExit']!=0:
            raise ValueError('actual existing success receipt required, not begin')
        witnesses[name]=dict(path=str(file.relative_to(ROOT)),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
                             source=item.get('source'),actualExit=item['actualExit'],reexecuted=False)
    introductions={}
    for file in (
        'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebDbPoolMetricRecorder.java',
        'src/deployment/monitoring/prometheus/debug.yml.template'):
        introductions[file]=subprocess.check_output(['git','log','--diff-filter=A','--format=%H','--',file],
                                                     cwd=ROOT,text=True).splitlines()
        if len(introductions[file])!=1:
            raise ValueError('unique actual first introduction, not inferred manufacture')
    static=subprocess.run([sys.executable,'-B','-m','pyflakes',str(Path(__file__))],
                          cwd=ROOT,text=True,capture_output=True,check=False)
    actual=0 if result.wasSuccessful() and result.testsRun==4 and not result.skipped and static.returncode==0 else 1
    verify(invocation)
    value=dict(actualExit=actual,source=source,invocation=invocation,
        timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),startUTC=started,
        environment=dict(os=platform.platform(),python=sys.version),
        testsRun=result.testsRun,failed=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
        static=dict(actualExit=static.returncode,command=static.args,stdout=static.stdout,stderr=static.stderr),
        log=log.getvalue(),queries=snapshots,originalWitnesses=witnesses,firstIntroductions=introductions,
        publicCorpusFileCount=len(entries),bugs=['BUG1686'],horizontal=['YKT1437'],
        correctedEvents=['PGPT-20261008-1959','PGPT-20261008-1960'],
        originalEstimateUnchanged=dict(low=.5,base=1.5,high=4),
        plannedManufactureDelta=0,plannedContractCompletionDelta=0,additionalVerificationCases=12,
        repeatGroupReclassified='SELECTION_REWORK_DUPLICATE_CONFIRMATION_NOT_NEW_PLANNED_PROGRESS',
        originalResultsRetained=True,productTestsExecutedByGuard=0,actualVmActions=0,
        actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,effortPercent=None,
        whole451Accepted=False,noApprovalInferredFromIndex=True)
    os.umask(0o077)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as handle:
        json.dump(value,handle,ensure_ascii=False,sort_keys=True,indent=2)
        handle.write('\n')
    print(json.dumps(dict(actualExit=actual,tests=result.testsRun,corpus=len(entries),
                         manifestSha256=hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest())))
    raise SystemExit(actual)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    selection=parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--query')
    selection.add_argument('--digest', action='append', metavar='SHA256')
    parser.add_argument('--source', metavar='GIT_COMMIT')
    args=parser.parse_args()
    if args.query is not None:
        if args.source is not None:
            parser.error('--source is only used with --digest')
        rows=index_entries(args.query,corpus())
        print(json.dumps(dict(query=args.query,totalMatches=len(rows),newest=rows[:15],acceptanceInferred=False),ensure_ascii=False))
    else:
        try:
            result=digest_candidates(ROOT,args.source,args.digest)
        except (ValueError, subprocess.CalledProcessError) as error:
            parser.error(f'digest lookup failed ({type(error).__name__})')
        print(json.dumps(result,ensure_ascii=False))
