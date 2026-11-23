"""Compare the tracked Artemis declarations with the independent SS321 capacity table."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PLANS = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
XML = Path("src/deployment/artemis/etc/broker.xml")
SS321 = next(Path("documents/300_SS/320_メッセージング").glob("321_*"))
CORE_NS = {"a": "urn:activemq:core"}

# SS321 §5.3: in-memory MiB/messages, paging MiB/messages and combined MiB/messages.
CAPACITY = {
    "nk.sync.request": (32, 50, 224, 450, 256, 500),
    "nk.sync.reply.web": (32, 50, 224, 450, 256, 500),
    "nk.async.work": (128, 1000, 896, 9000, 1024, 10000),
    "nk.web.log": (64, 1000, 192, 9000, 256, 10000),
    "nk.dead.letter": (128, 1000, 1920, 9000, 2048, 10000),
    "nk.expiry": (64, 1000, 960, 9000, 1024, 10000),
}
COMMON = {
    "dead-letter-address": "nk.dead.letter",
    "expiry-address": "nk.expiry",
    "auto-create-dead-letter-resources": "false",
    "auto-create-expiry-resources": "false",
    "auto-create-addresses": "false",
    "auto-create-queues": "false",
    "auto-delete-addresses": "false",
    "auto-delete-queues": "false",
    "address-full-policy": "PAGE",
    "page-full-policy": "FAIL",
    "disk-full-policy": "BLOCK",
    "page-size-bytes": "8MiB",
    "max-read-page-bytes": "16MiB",
    "max-read-page-messages": "100",
    "redelivery-collision-avoidance-factor": "0.0",
    "enable-metrics": "true",
    "enable-ingress-timestamp": "true",
}


def git(*args):
    return subprocess.check_output(["git", *args], timeout=25)


def pin(path):
    return dict(path=str(path), sha256=sha256(Path(path).read_bytes()).hexdigest())


def read(path):
    return json.loads(Path(path).read_bytes())


def node(parent, path):
    elements = parent.findall(path, CORE_NS)
    result, = elements
    return result


def value(parent, tag):
    return node(parent, f"a:{tag}").text


def main():
    checkpoint, = PLANS.glob("3429_*")
    state = read(checkpoint)
    group = state["values"]
    source, core = group["source"], group["productionCoreMain"]
    assert git("rev-parse", "HEAD").decode().strip() == source
    body = XML.read_bytes()
    assert body == git("show", f"{core}:{XML}") == git("show", f"{source}:{XML}")
    design_ref = group["canonicalDesignSource"]
    design = git("show", f"{design_ref}:{SS321}").decode()
    assert all(f"| `{name}` | `{name}.q` | ○ |" in design for name in CAPACITY)
    for name, (mem, messages, disk, paged, _, _) in CAPACITY.items():
        def formatted(count):
            return f"{count:,}"
        assert (
            f"| `{name}` | {formatted(mem)}MiB / {formatted(messages)} |"
            f" {formatted(disk)}MiB / {formatted(paged)} |"
        ) in design
    conf = node(ET.fromstring(body), "a:core")
    assert value(conf, "global-max-size") == "512MiB"
    addresses = node(conf, "a:addresses")
    settings = node(conf, "a:address-settings")
    by_name = {a.get("name"): a for a in addresses.findall("a:address", CORE_NS)}
    policies = {a.get("match"): a for a in settings.findall("a:address-setting", CORE_NS)}
    assert len(addresses) == len(by_name) == len(settings) == len(policies) == len(CAPACITY)
    assert set(by_name) == set(policies) == set(CAPACITY)
    rows = []
    for name, (mem, messages, disk, paged, total, count) in CAPACITY.items():
        address = by_name[name]
        anycast = node(address, "a:anycast")
        assert len(address) == len(anycast) == 1
        queue = node(anycast, "a:queue")
        assert queue.get("name") == f"{name}.q"
        policy = policies[name]
        observed = {
            "max-size-bytes": f"{mem}MiB",
            "max-size-messages": str(messages),
            "page-limit-bytes": f"{disk}MiB",
            "page-limit-messages": str(paged),
        }
        assert all(value(policy, tag) == expected for tag, expected in (COMMON | observed).items())
        assert mem + disk == total and messages + paged == count
        rows.append(dict(address=name, queue=queue.get("name"), routing="ANYCAST",
                         memoryMiB=mem, memoryMessages=messages, pagingMiB=disk,
                         pagingMessages=paged, combinedMiB=total, combinedMessages=count))
    assert sum(x["memoryMiB"] for x in rows) == 448
    assert sum(x["combinedMiB"] for x in rows) == 4864

    ordinary, = OPS.glob("PG42624*/manifest.json")
    lineage, = OPS.glob("PG43046*/manifest.json")
    past = read(ordinary)
    chain = read(lineage)
    assert past["actualExit"] == chain["actualExit"] == 0
    assert pin(ordinary) in chain["originalProofs"]
    protocol = "src/schubert-nk-protocol"
    assert git("rev-parse", f"{core}:{protocol}").decode().strip() == chain["sameProtocolTree"]
    cases = past["sanitizedCases"]
    assert pin(cases["path"]) == cases
    current_scope = [x for x in read(cases["path"]) if x["className"].endswith(".BrokerTopologyTest")]
    assert len(current_scope) == 2 and all(x["outcome"] == "PASS" for x in current_scope)
    out = OPS / group["run"]
    out.mkdir()
    records = dict(run=group["run"], source=source, productCore=core, startEvent=state["eventId"],
        actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), wbs="WBS-P005-01/2",
        design=dict(path=str(SS321), source=design_ref, sha256=sha256(design.encode()).hexdigest()),
        trackedBroker=pin(XML), addresses=rows, globalMemoryMiB=512, perAddressMemoryMiB=448, combinedMiB=4864,
        observedCommon=COMMON, reusedProtocolCases=current_scope, prior=[pin(ordinary),pin(lineage),cases],
        declaredQueueCount=len(rows), actualDurableQueuesObserved=0, actualRoleChecks=0,
        actualBrokerActions=0, productTestsReplayed=0, whole451=False, formalAcceptanceId=None,
        outstanding=["effective durable queues and ACL", "runtime data/paging/expiry behavior", "formal build and 451"])
    with (out/"manifest.json").open("x") as dst:
        dst.write(json.dumps(records,indent=2)+"\n")
    print(len(rows),len(COMMON),len(current_scope))


if __name__ == "__main__":
    main()
