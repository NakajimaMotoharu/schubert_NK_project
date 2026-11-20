"""Reconcile the literal findings and the known Controller source inventory."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
CANONICAL = "63c4a673bc98464a5bb8e9dae85eba3ce9ef0d2a"
DESIGN = "documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md"
MODULE = Path("src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web")
EXPECTED = tuple(("JmsRequestSender ArtemisRequestSender ReplyCorrelationRegistry "
                  "JmsContextFactory WebBrokerContexts ArtemisReplyConsumer ArtemisReplyConsumers "
                  "JmsReplyDecoder ArtemisReplyDlqSender PendingReply").split())
OLD = "JmsRequestReplyClient"
CASE_ROOT = "dev.codex.schubert.nk.web."
RULE = "CONTROLLER_BOUNDARY"


def pin(p):
    return dict(path=str(p),sha256=sha256(p.read_bytes()).hexdigest())


def git(*parts):
    return subprocess.check_output(["git",*parts],timeout=30)


def find(prefix, file="manifest.json"):
    path, = OPS.glob(f"{prefix}-*/{file}")
    return path


def findings(receipt):
    shape = json.loads(receipt.read_bytes())
    path = receipt.with_name("audit.stdout.txt")
    assert pin(path) == shape["steps"]["audit"]["stdout"]
    records = [tuple(row.split("\t")[1:]) for row in path.read_text().splitlines()
               if row.startswith("FINDING\t")]
    assert len(records) == len(set(records))
    return set(records)


def main():
    old, red, green = find("PG41064"),find("PG41092"),find("PG41098")
    preflight = find("PG41096","preflight-receipt.json")
    status = json.loads(green.read_bytes())
    seen = findings(green)
    assert not findings(red) and len(seen) == 67 and len(findings(old)) == 57
    new = seen - findings(old)
    assert len(new) == 10 and all(rule == RULE and origin.startswith(CASE_ROOT+"fence.Owner")
                                  for rule,origin,target in new)
    assert {target.split(".")[-1].split("$",1)[0] for _,_,target in new} == set(EXPECTED)
    assert status["correctedPathFixture"]["testId"] == "PT-F02-PATH-IO-007"
    assert status["correctedPathFixture"]["actualFindings"] == 0
    cs = status["productionCore"]
    design = git("show",f"{CANONICAL}:{DESIGN}")
    assert "Controllerからは画面単位facadeを呼び".encode() in design
    listed = git("ls-tree","-r","--name-only",cs,"--",str(MODULE/"controller")).decode().splitlines()
    pattern = re.compile(r"\b(?:" + "|".join((*EXPECTED,OLD)) + r")\b")
    controller_source = []
    for name in listed:
        assert name.endswith(".java")
        path = Path(name)
        data = git("show",f"{cs}:{name}")
        assert data == path.read_bytes()
        assert not pattern.search(data.decode()), name
        controller_source.append(pin(path))
    assert len(controller_source) >= 10
    names = set()
    for name in (*EXPECTED, OLD):
        path = MODULE/"messaging"/(name+".java")
        assert git("show",f"{cs}:{path}") == path.read_bytes()
        names.add(name)
    out = OPS/"PG41100-f02-web-transport-source-independent-v1"
    out.mkdir()
    p = out/"manifest.json"
    with p.open("x") as f:
        json.dump(dict(actualExit=0,productionCore=cs,toolSource=status["toolSource"], prior=pin(old),
                       red=pin(red), green=pin(green), preflight=pin(preflight), canaries=13,
                       priorControls=90, correctedPathField=1, exactDesignSha256=sha256(design).hexdigest(),
                       canonicalDesign=CANONICAL, controllerSourcePins=controller_source,
                       fixedTransportNames=sorted(names), sourceNameMentions=0, directRuntimeProof=False,
                       productBytecodeRead=0, nativeOrJmsOperations=0, productTests=0, wholeF02=False,
                       formalDelta=0, whole451=False, terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  f,indent=2,ensure_ascii=False)
        f.write("\n")
    print(pin(p),len(controller_source))


if __name__=="__main__":
    main()
