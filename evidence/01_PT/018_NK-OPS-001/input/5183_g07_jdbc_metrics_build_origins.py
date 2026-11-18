"""Prove remaining scanner hits against owned compiled bytes and pinned public SDK artifacts."""
from collections import Counter
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re

spec=spec_from_file_location("proof",Path(__file__).with_name("5182_g07_jdbc_metrics_cached_classification.py"))
p=module_from_spec(spec)
spec.loader.exec_module(p)
B, t, OUT, WORK = p.B, p.t, p.OUT, p.WORK
TC=Path.cwd().parent/"toolchain"
JAR_REPORTS={
    "PG39440-service-jdbc-spotbugs-current-peers-v1",
    "PG39460-ssc468-admission-ports-static-v1",
    "PG39463-ssc468-admission-ports-static-v2",
}
COMPILE_REPORTS={
    "PG39434-service-jdbc-four-module-build-v1",
    "PG39458-admission-single-cleanup-four-build-v1",
    "PG39462-admission-single-cleanup-four-build-v2",
}
ADMITTED_CLASS_DIGESTS={
    "AesCredentialFile","ApiNonSecretConfig","ExistingFileAccess",
    "InspectorAesCredential","InspectorCredentialAccess","InspectorCredentialException",
    "InspectorCredentialLoader","InspectorDbCredential","MorningDatabaseSession$Access",
    "MorningStartupLaunchOwner$ApiRetained","NonSecretConfigSource","RootBatchCredentialReader",
    "RootServiceCredentialSource","ServiceCredentialException","ServiceCredentialLocation",
    "ServiceCredentialReader","ServiceCredentialSet","WebNonSecretConfig",
}


def exact_build_class(path,key,sha):
    expected=Path(key)
    if expected.stem not in ADMITTED_CLASS_DIGESTS:
        return None
    assert expected.parts[:4]==("dev","codex","schubert","nk") and expected.suffix==".class"
    assert ".." not in expected.parts and expected.stem.split("$")[0] not in B.HELD
    assert path.parent.name=="compile" and path.parent.parent.name in COMPILE_REPORTS
    m=B.load(path)
    assert m["actualExit"]==0 and m["inputHashesReverified"] and m["productTestsExecuted"]==0
    matched=[name for name,classes in m["physicalClassHashes"].items() if classes.get(key)==sha]
    assert len(matched)==1 and matched[0] in ("protocol","storage","bootstrap","batch")
    artifact=Path(m["cwd"])/f"src/schubert-nk-{matched[0]}/target/classes"/expected
    assert artifact.is_relative_to(t.RUNS) and artifact.is_file() and artifact.resolve()==artifact
    assert B.ref(artifact)["sha256"]==sha
    return dict(kind="Fixed four-module build class digest, no class initialization",
          compiledClass=key,module=matched[0],fixedCompile=B.ref(path))


def exact_tool_runtime(path,key,sha):
    if path.parent.name not in JAR_REPORTS:
        return None
    part=Path(key)
    assert part.suffix==".jar" and part.is_relative_to(TC/"m2/repository") and part.resolve()==part
    assert "/dev/codex/schubert/" not in key
    manifest=B.load(path)
    assert manifest["toolHashes"][key]==sha and B.ref(part)["sha256"]==sha
    pin=manifest.get("runtimeReference",manifest.get("runtime"))
    runtime=Path(pin["path"])
    assert B.ref(runtime)==pin
    base=B.load(runtime)
    dependency_groups = (base["toolRuntimeHashes"],base["auxiliaryClasspathHashes"])
    assert any(group.get(key)==sha for group in dependency_groups) and key not in base["currentJarHashes"]
    return dict(kind="Fixed public dependency JAR content digest",
        dependencyPath=key,toolReport=B.ref(path),runtime=B.ref(runtime))


def main():
    initial=OUT/"qualified-cached-initial.json"
    results=B.load(initial)
    prior=OUT/"remaining-origins.json"
    pending=B.load(prior)
    assert len(pending)==results["unresolvedCandidates"] and B.ref(prior)==results["unclassified"]
    scan=B.load(OUT/"scan-terminal.json")
    assert B.ref(WORK/"projection.json")["sha256"]==scan["projectionSha256"]
    indexed={(r["path"],r["blobOid"]):r for r in B.load(WORK/"projection.json")}
    qualified=[]; remaining=[]
    for row in pending:
        v=indexed[row["path"],row["blob"]]
        path=Path(row["path"])
        line=p.projection_lines(WORK/v["relativeProjection"],v["decodedSha256"])[row["line"]-1]
        assert B.sha(line)==row["lineSha256"]
        match=t.FIELD.fullmatch(line)
        assert match is not None and row["rule"]=="generic-api-key"
        assert max(match.start(2),row["startColumn"]-1)<min(match.end(2),row["endColumn"])
        key,sha=(x.decode() for x in match.groups())
        assert len(sha)==64
        # The current tracked manifest must be byte identical to the scanned Git version.
        assert B.ref(path)["sha256"]==v["blobSha256"]
        origin=exact_build_class(path,key,sha) or exact_tool_runtime(path,key,sha)
        if origin:
            qualified.append(dict(row,ground=origin))
        else:
            remaining.append(row)
    categories=Counter(results["categories"])
    categories.update(r["ground"]["kind"] for r in qualified)
    assert sum(categories.values())+len(remaining)==scan["findingsCount"]
    closed=OUT/"additional-build-origins.json"
    open_path=OUT/"remaining-after-build-origins.json"
    B.write(closed,qualified)
    B.write(open_path,remaining)
    manifest=dict(results,categories=dict(categories),unresolvedCandidates=len(remaining),
       confirmedSecrets=0 if not remaining else None, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
       originalClassification=B.ref(initial),additionalBuildOrigins=B.ref(closed),remaining=B.ref(open_path),
       resultQualifiedForRange=not remaining and not results["unqualifiedBinary"])
    B.write(OUT/"qualified-final-private-detail.json",manifest)
    print(dict(classification=dict(categories),pending=len(remaining),binary=results["unqualifiedBinary"]))


if __name__=="__main__":
    main()
