"""Reproduce and verify the Web log codec constructor copy ordering."""

from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[4]
TC = ROOT.parent / "toolchain"
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
EVIDENCE = ROOT / "evidence/01_PT/006_NK-MSG-002/evidence"
WORK = ROOT.parent / "pgpt-runs/PG379"
MODULE = Path("src/schubert-nk-web")
PACKAGE = "dev.codex.schubert.nk.web.logging"
REL = Path(PACKAGE.replace(".", "/"))
MAIN_FILES = ("WebLogPayloadCodec.java", "WebLogPayloadIdentity.java", "WebLogPayloadException.java",
              "EncryptedWebLogPayload.java", "package-info.java")
TEST_CLASS = PACKAGE + ".WebLogPayloadCodecTest"
TEST_FILE = MODULE / "src/test/java" / REL / "WebLogPayloadCodecTest.java"
METHOD = "invalidConfigurationPreservesFailureOrderAndBorrowedKeys"
SECOND_METHOD = "preservesBothOwnedKeyVersionsAfterCallerChangesInputs"
EXPECTED = ("bug036CallerMonitorCannotBlockEncryptionDecryptionOrClose",
            "canonicalAadAndFullEnvelopeMatchIndependentVectorAndCopiesAreDefensive",
            "currentWritesPreviousReadsAndUnknownKeyDenyClosed",
            "malformedEnvelopeMagicVersionKeyIdLengthNonceCiphertextAndTagAreRejected",
            "everyAadFieldMutationAndCrossRowMoveFailAuthenticationBeforeAnyPlaintext",
            "exact2336ByteWireHeaderIdentityAndPayloadSemanticsAreCheckedBeforeStorageAndAfterAuth",
            "modelBoundsConfigurationNullAndClosedLifecycleFailExplicitly",
            "concurrentProductionNonceGenerationKeepsEveryMessageAuthenticAndDistinct",
            "unavailableCipherProviderHasBoundedFailureAndNoRawProviderCause",
            "weblogOwn001NonceErrorThenOtherWorkerMatchesIndependentGolden", METHOD)


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    return {"path": str(path), "sha256": sha(path.read_bytes())}


def load(path):
    return json.loads(path.read_bytes())


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], cwd=ROOT, timeout=30)


def inspect(binary):
    start = binary.index("  " + PACKAGE + ".WebLogPayloadCodec(java.lang.String, byte[], java.lang.String, byte[], java.security.SecureRandom);")
    end = binary.index("\n  public ", start)
    return binary[start:end].splitlines()


def instructions(lines):
    found = {}
    for line in lines:
        match = re.match(r"^\s*(\d+):\s+(\S+)\s*(.*)$", line)
        if match:
            found[int(match[1])] = (match[2], match[3])
    return found


def select(bytecode, needle):
    return [index for index, (_, description) in bytecode.items() if needle in description]


def decisive_instructions(bytecode, baseline):
    key_calls = select(bytecode, "Method requireKey:")
    random_check = select(bytecode, "String random")
    duplicate = select(bytecode, "String web log key versions must be distinct")
    assert len(key_calls) == 2 and len(random_check) == len(duplicate) == 1
    assert key_calls[0] < duplicate[0] < random_check[0]
    if baseline:
        assert not select(bytecode, 'clone:')
        return dict(keyValidationCalls=key_calls, duplicate=duplicate[0], random=random_check[0])
    clone = select(bytecode, "clone:")
    erasure = select(bytecode, "java/util/Arrays.fill:([BB)V")
    assert len(clone) == 2 and len(erasure) == 1
    assert random_check[0] < clone[0] < clone[1] < erasure[0]
    return dict(keyValidationCalls=key_calls, randomCheckLiteral=random_check[0],
                clonedOnlyAfterAllValidation=clone, errorHandlerErasure=erasure[0])


def main():
    mode = sys.argv[1]
    assert mode in ("baseline", "qualified", "single")
    baseline = mode == "baseline"
    single = mode == "single"
    run = {
        "baseline": "PG41348-p01810-web-log-constructor-ownership-v1",
        "qualified": "PG41350-p01810-web-log-constructor-qualified-v1",
        "single": "PG41354-p01810-web-log-single-ownership-v1",
    }[mode]
    work = WORK / run
    work.mkdir(mode=0o700)
    source = git("rev-parse", "HEAD").decode().strip()
    evidence, = OPS.glob("PG41306*/manifest.json")
    library = load(evidence)["retained"]["localJar.jar"]
    archive = Path(library["path"])
    assert pin(archive) == library
    assert not git("diff", "--name-only", "62b239d4da", source, "--", "src/schubert-nk-protocol", "pom.xml")
    source_dir = work / "src/main/java" / REL
    source_dir.mkdir(parents=True)
    inputs = []
    for filename in MAIN_FILES:
        relative = MODULE / "src/main/java" / REL / filename
        data = git("show", f"{source}:{relative}")
        assert data == (ROOT / relative).read_bytes()
        (source_dir / filename).write_bytes(data)
        inputs.append(dict(path=str(relative), sha256=sha(data)))
    test_source = work / TEST_FILE.name
    test_bytes = git("show", f"{source}:{TEST_FILE}")
    assert test_bytes == (ROOT / TEST_FILE).read_bytes()
    test_source.write_bytes(test_bytes)
    compile_policy = git("show", f"{source}:pom.xml")
    uri = "http://maven.apache.org/POM/4.0.0"
    ET.register_namespace("", uri)
    ns = {"p": uri}
    parent = ET.fromstring(compile_policy)
    compiler, = [p for p in parent.findall("./p:build/p:plugins/p:plugin", ns)
                 if p.findtext("p:artifactId", namespaces=ns) == "maven-compiler-plugin"]
    assert b"-Xep:NullAway:ERROR" in ET.tostring(compiler)
    assert b"-Werror" in ET.tostring(compiler)

    def set_value(p, key, value=None):
        child = ET.SubElement(p, "{" + uri + "}" + key)
        child.text = value
        return child

    pom = ET.Element("{" + uri + "}project")
    for field, value in (("modelVersion", "4.0.0"), ("groupId", "dev.codex.schubert.quality"),
                         ("artifactId", "pgpt-weblog-key-phase"), ("version", "1")):
        set_value(pom, field, value)
    prop = set_value(pom, "properties")
    for key in ("maven.compiler.release", "project.build.sourceEncoding", "error-prone.version", "nullaway.version"):
        set_value(prop, key, parent.findtext("p:properties/p:" + key, namespaces=ns))
    dependency = set_value(pom, "dependencies")
    for values in (dict(groupId="org.jspecify", artifactId="jspecify", version="1.0.1"),
                   dict(groupId="dev.codex.schubert", artifactId="current-protocol", version="1",
                        scope="system", systemPath=str(archive))):
        dep = set_value(dependency, "dependency")
        for key, value in values.items():
            set_value(dep, key, value)
    set_value(set_value(pom, "build"), "plugins").append(deepcopy(compiler))
    xml = work / "pom.xml"
    ET.ElementTree(pom).write(xml, encoding="utf-8", xml_declaration=True)
    jdk = TC / "jdk-25.0.4/bin"
    mvn = TC / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    repo = TC / "m2/repository"
    env = {"JAVA_HOME": str(jdk.parent), "PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    steps = {}

    def execute(name, arguments):
        argv = list(map(str, arguments))
        done = subprocess.run(argv, cwd=work, env=env, timeout=125, check=False, capture_output=True)
        stdout, stderr = work / (name + ".stdout"), work / (name + ".stderr")
        stdout.write_bytes(done.stdout)
        stderr.write_bytes(done.stderr)
        steps[name] = dict(argv=argv, exit=done.returncode, stdout=pin(stdout), stderr=pin(stderr))
        save(work / (name + "-terminal.json"), steps[name])
        assert done.returncode == 0, (name, done.stderr[-600:])
        return stdout

    execute("compile", [mvn, "-o", "-B", "-ntp", "-f", xml,
                        "-Dmaven.repo.local=" + str(repo), "-Dmaven.test.skip=true", "compile"])
    classes = work / "target/classes"
    classifier = classes / REL / "WebLogPayloadCodec.class"
    javap = execute("javap", [jdk / "javap", "-c", "-p", "-s", classifier])
    bytecode = javap.read_text()
    construct = inspect(bytecode)
    code = instructions(construct)
    if single:
        copies = select(code, "java/lang/System.arraycopy:")
        allocated = [i for i, (op, _) in code.items() if op == "newarray"]
        random, = select(code, "String random")
        random_field, = select(code, "Field random:")
        validation = select(code, "Method requireKey:")
        duplicate, = select(code, "String web log key versions must be distinct")
        assert len(validation) == len(copies) == 2 and len(allocated) == 1
        assert max(validation) < duplicate < random < random_field < allocated[0] < min(copies)
        assert "Exception table:" not in "\n".join(construct) and not select(code, "clone:")
        proof = dict(keyValidationCalls=validation, finalValidation=random_field,
                     ownedKeyAllocations=allocated, boundedArrayCopyCalls=copies)
    else:
        proof = decisive_instructions(code, baseline)
    if baseline:
        assert re.search(r"private static byte\[\] requireKey.*?clone:", bytecode, re.DOTALL)
        proof["firstKeyCopyAcquiredBeforeLaterValidationAndNoConstructorHandler"] = "Exception table:" not in "\n".join(construct)
        assert proof["firstKeyCopyAcquiredBeforeLaterValidationAndNoConstructorHandler"]
    else:
        if not single:
            table = re.findall(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class java/lang/Error$", "\n".join(construct), re.MULTILINE)
            (first, after, entry), = [tuple(map(int, fields)) for fields in table]
            one, two = proof["clonedOnlyAfterAllValidation"]
            assert one < first <= two < after < entry <= proof["errorHandlerErasure"]
            proof["constructorErrorRange"] = [first, after, entry]
            assert any(line.rstrip().endswith("athrow") for line in construct)
        junit = TC / "junit-platform-console-standalone-1.13.4.jar"
        anno = repo / "org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
        agent = repo / "org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
        test_classes = work / "tests"
        test_classes.mkdir()
        cp = os.pathsep.join(map(str, (classes, archive, anno, junit)))
        execute("compile-test", [jdk / "javac", "--release", "25", "-Xlint:all", "-Werror",
                                 "-cp", cp, "-d", test_classes, test_source])
        execute("junit", [jdk / "java", "-javaagent:" + str(agent) + "=destfile=" + str(work / "unit.exec") +
                         ",sessionid=" + run, "-cp", str(test_classes) + os.pathsep + cp,
                         "org.junit.platform.console.ConsoleLauncher", "execute", "--disable-ansi-colors",
                         "--select-class", TEST_CLASS, "--fail-if-no-tests", "--reports-dir", work / "reports"])
        raw = work / "reports/TEST-junit-jupiter.xml"
        outcome = ET.parse(raw).getroot()
        selected = (*EXPECTED, SECOND_METHOD) if single else EXPECTED
        expected = Counter(name + "()" for name in selected)
        assert Counter(row.get("name") for row in outcome.findall("testcase")) == expected
        assert all(int(outcome.get(attr)) == 0 for attr in ("failures", "errors", "skipped"))
        assert int(outcome.get("tests")) == len(expected)
        proof.update(xml=pin(raw), exec=pin(work / "unit.exec"), productTests=len(expected),
                     noFailuresErrorsOrSkips=True, constructorTest=METHOD)
    dest = EVIDENCE / run
    dest.mkdir()
    save(dest / "manifest.json", dict(
        run=run, actualExit=0, terminalAtUTC=utc(), source=source, mode=mode, sourceInputs=inputs,
        protocolPackage=library, protocolReference=pin(evidence), compilerSettingsSha256=sha(ET.tostring(compiler)),
        pom=pin(xml), testSourceSha256=sha(test_bytes), classfile=pin(classifier),
        steps=steps, bytecodeProof=proof, openedRealSecrets=0, externalOperations=0,
        invokedRawAllocationFailure=False, whole451=False, formalDelta=0
    ))
    print(run, proof)


if __name__ == "__main__":
    main()
