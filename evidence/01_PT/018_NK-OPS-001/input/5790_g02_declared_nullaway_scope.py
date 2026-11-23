"""Audit the six static compiler declarations and named local compile receipts."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET


CORE = "87927ea17c1c8dbef528bc0c6882c24b1fe7c871"
EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
RUN = "PG43172-g02-nullaway-declared-scope-v1"
NS = {"m": "http://maven.apache.org/POM/4.0.0"}
MODULES = ("api", "batch", "bootstrap", "protocol", "storage", "web")
PREFIX = "dev.codex.schubert.nk"
PARENT_OPTIONS = (
    "-Xep:NullAway:ERROR",
    "-XepOpt:NullAway:AnnotatedPackages=" + PREFIX,
    "-XepOpt:NullAway:JSpecifyMode=true",
    "-XepOpt:NullAway:JSpecifyJDKModels=true",
)


def git(*argv):
    return subprocess.check_output(["git", *argv])


def git_file(source, path):
    return git("show", f"{source}:{path}")


def pin(path, content=None):
    if content is None:
        content = Path(path).read_bytes()
    return {"path": str(path), "sha256": sha256(content).hexdigest()}


def find(tree, path):
    return tree.find(path, NS)


def value(tree, path):
    result = find(tree, path)
    return result.text.strip() if result is not None and result.text is not None else None


def compiler(tree):
    matches = [
        plugin for plugin in tree.findall("m:build/m:plugins/m:plugin", NS)
        if value(plugin, "m:artifactId") == "maven-compiler-plugin"
    ]
    assert len(matches) == 1
    return matches[0]


def default_compile(plugin):
    matches = [
        run for run in plugin.findall("m:executions/m:execution", NS)
        if value(run, "m:id") == "default-compile"
    ]
    assert len(matches) == 1
    return matches[0]


def parent_declaration(old_core):
    path = Path("pom.xml")
    raw = git_file(CORE, path)
    tree = ET.fromstring(raw)
    plug = compiler(tree)
    declaration = default_compile(plug)
    old = default_compile(compiler(ET.fromstring(git_file(old_core, path))))
    assert ET.tostring(old) == ET.tostring(declaration)
    assert value(declaration, "m:inherited") != "false"
    args = find(declaration, "m:configuration/m:compilerArgs")
    assert args is not None and args.attrib == {"combine.self": "override"}
    arguments = [arg.text.strip() for arg in args]
    options = [arg.split() for arg in arguments if arg.startswith("-Xplugin:ErrorProne")]
    assert len(options) == 1 and all(item in options[0] for item in PARENT_OPTIONS)
    props = {
        x: value(tree, "m:properties/m:" + x)
        for x in ("maven.compiler.release", "error-prone.version", "nullaway.version", "jspecify.version")
    }
    assert props == {
        "maven.compiler.release": "25",
        "error-prone.version": "2.50.0",
        "nullaway.version": "0.14.1",
        "jspecify.version": "1.0.1",
    }
    return dict(input=pin(path, raw), comparedParentSource=old_core,
                defaultCompileUnchanged=True, packages=PREFIX, options=PARENT_OPTIONS, versions=props)


def module_declaration(module, file_paths):
    location = f"src/schubert-nk-{module}"
    path = Path(location) / "pom.xml"
    raw = git_file(CORE, path)
    tree = ET.fromstring(raw)
    assert value(tree, "m:parent/m:artifactId") == "schubert-nk"
    assert value(tree, "m:parent/m:relativePath") == "../../pom.xml"
    assert value(tree, "m:properties/m:maven.compiler.release") == "25"
    assert find(tree, "m:profiles") is None and find(tree, "m:build/m:sourceDirectory") is None
    plug = compiler(tree)
    assert not any(value(run, "m:id") == "default-compile"
                   for run in plug.findall("m:executions/m:execution", NS))
    assert find(plug, "m:configuration/m:skipMain") is None
    assert find(plug, "m:configuration/m:excludes") is None
    prefix = location + "/src/main/java/"
    paths = {path for path in file_paths if path.startswith(prefix) and path.endswith(".java")}
    assert paths and all(path.removeprefix(prefix).startswith(PREFIX.replace(".", "/") + "/")
                         for path in paths)
    package_paths = sum(Path(path).name == "package-info.java" for path in paths)
    return paths, dict(module=module, pom=pin(path, raw), inInheritedPrefixPaths=len(paths),
                       packageInfoPaths=package_paths, otherJavaPaths=len(paths) - package_paths,
                       overridingDefaultCompileExecution=False, sourcePathOutsidePrefix=0)


def receipt(tag):
    path, = EVIDENCE.glob(tag + "*/manifest.json")
    return path, json.loads(path.read_bytes())


def exact_compile_inputs(paths, own_tags):
    proofs = []
    input_paths = set()
    for tag in own_tags:
        path, record = receipt(tag)
        assert record["productCore"] == CORE and record["mavenExit"] == record["actualExit"] == 0
        files = record["sourceInputs"]
        for reference in files:
            src = reference["path"]
            assert src in paths and pin(src, git_file(CORE, src)) == reference
            input_paths.add(src)
        proofs.append(dict(receipt=pin(path), verifiedInputs=len(files)))
    return proofs, input_paths


def main():
    all_paths = git("ls-tree", "-rz", "--name-only", CORE, "--", "src").decode().split("\0")
    old_path, old = receipt("PG41330")
    prior_jar_path, prior_jar = receipt("PG43066")
    assert prior_jar["productCore"] == CORE and prior_jar["actualExit"] == 0
    parent = parent_declaration(old["core"])
    declarations = []
    paths = set()
    for module in MODULES:
        java, declaration = module_declaration(module, all_paths)
        assert not paths.intersection(java)
        paths.update(java)
        declarations.append(declaration)
    assert paths == {path for path in all_paths if "/src/main/java/" in path and path.endswith(".java")}
    proofs, compile_inputs = exact_compile_inputs(paths, ("PG43132", "PG43146", "PG43160"))
    baselines = Counter(Path(path).parts[1] for path in compile_inputs if Path(path).name != "package-info.java")
    out = EVIDENCE / RUN / "manifest.json"
    out.parent.mkdir()
    record = dict(
        run=RUN, wbs="WBS-G02", actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
        source=git("rev-parse", "HEAD").decode().strip(), productCore=CORE,
        verifier=pin(Path(__file__).relative_to(Path.cwd())), coveragePathMeaning="Tracked paths; package statements not compiled or inferred as runtime coverage",
        parent=parent, declaredProductCounts=declarations, totalDeclaredJavaSourcePaths=len(paths),
        historicalCompilerEvidence=pin(old_path),
        currentNormalArtifactIndex=pin(prior_jar_path), currentNormalProductArtifactModules=sorted(prior_jar["normalArtifacts"]),
        namedRecentCompileProofs=proofs, scopedExactProductionTypes=baselines,
        scopedExactCompilerInputPaths=len(compile_inputs),
        actualCompilesInvoked=0, productPtExecutions=0, wholeG02=False,
        whole451=False, formalAcceptanceId=None,
    )
    with out.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(len(paths), dict(baselines), pin(out))


if __name__ == "__main__":
    main()
