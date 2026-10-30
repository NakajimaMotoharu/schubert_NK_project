import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { replaceExactlyOnce } from "./literal_template_replace_v1.mjs";

// BUG2113/YKT1860: reads one frozen public tool and prints an apply_patch; writes no files.
let source = readFileSync(new URL("./pg14846_named_dto_existing_exec_post.py", import.meta.url), "utf8");
assert.equal(createHash("sha256").update(source).digest("hex"), "29d5a3b2d557b1ea20dbf271abfd0efe5cd9af66665d565adf0582c7b3e5b448");
const once = (needle, replacement) => { source = replaceExactlyOnce(source, needle, replacement); };
once('"""Saved same-source original31 only: qualify all69 independent named DTO Sources without Product replay."""', '"""Saved original31 only: seven carrier Source closures, true interfaces versus standard filtered records."""');
once("OUT=data.BASE/'PG14846-named-dto-existing-exec-post-v1'", "OUT=data.BASE/'PG14862-protocol-carrier-seven-existing-post-v1'");
once("SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14846-named-dto-existing-exec-post-v1'", "SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14862-protocol-carrier-seven-existing-post-v1'");
const first = source.indexOf("_fixture_path=");
const last = source.indexOf("TOTAL=31", first);
assert(first >= 0 && last > first);
source = source.slice(0, first) + String.raw`_relative_names=['FieldValue','FieldValueSet','LayoutPayload','PayloadData','PayloadRecord','semantic/ProtocolId','semantic/WireEnum']
SOURCES={PREFIX+name:_normal['begin']['inputHashes']['src/schubert-nk-protocol/src/main/java/'+PREFIX+name+'.java'] for name in _relative_names}
CLOSURES={name:({name,*[name+'$'+v for v in ['Text','Numeric','Flag','Unset']]} if name==PREFIX+'FieldValue' else {name}) for name in SOURCES}
NAMES=set().union(*CLOSURES.values())
TRUE_NO_CODE={PREFIX+name for name in ['FieldValue','LayoutPayload','PayloadData','PayloadRecord','semantic/ProtocolId','semantic/WireEnum']}
GENERATED_RECORD_CANDIDATES={PREFIX+'FieldValue$Numeric',PREFIX+'FieldValue$Flag'}
METADATA=set(TRUE_NO_CODE)
EXECUTABLE=NAMES-METADATA
` + source.slice(last);
once("def main():\n    invocation=", "def main():\n    global METADATA,EXECUTABLE\n    invocation=");
once("registry=data.read_checked(data.BASE/'PG14836-current908-resource-registry-v1/manifest.json','af91672ea724386906cce9ad70ae6e85e33f68455fcc14db020715da5b0033dd')", "registry=data.read_checked(data.BASE/'PG14852-current908-named69-registry-v1/manifest.json','46d6f90a7c719ef536105cd9233c5653c834291255e04f10dbdf58334d41345a')");
once("            assert any(m['hasCode'] for m in parsed['methods']) and parsed['sourceFile']==name.rsplit('/',1)[1]+'.java'\n            if name in METADATA:raise ValueError('unexpected generated metadata in these complete target closures')", String.raw`            assert parsed['sourceFile']==name.split('$',1)[0].rsplit('/',1)[1]+'.java'
            if name in TRUE_NO_CODE:assert parsed['flags']==1537 and not any(m['hasCode'] for m in parsed['methods'])
            else:assert any(m['hasCode'] for m in parsed['methods'])
            if name in GENERATED_RECORD_CANDIDATES:assert parsed['flags']==49 and {m['name'] for m in parsed['methods']}=={'<init>','toString','hashCode','equals','value'}`);
once("    expected_owners={name:'WBS-P001-03' for name in SOURCES}", "    expected_owners={PREFIX+name:('WBS-P002-01' if name.startswith('semantic/') else 'WBS-P001-03' if name in ['PayloadData','PayloadRecord'] else 'WBS-P001-02') for name in _relative_names}");
const inventory = String.raw`    inventory_tool=data.ROOT/'tools/quality/architecture/ProtocolCarrierCounterInventory.java'
    inventory_pin='c8731811e5987d53695756ceeb03bdb77b6415f76ebd84a96478e5ddedb4d978'
    assert data.sha(inventory_tool.read_bytes())==inventory_pin
    inventory_classes=SLOT/'inventory-classes';inventory_classes.mkdir()
    for label,command in [('inventory-tool-compile',[str(jdk/'javac'),'-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(inventory_classes),str(inventory_tool)]),('counter-inventory',[str(jdk/'java'),'-cp',str(inventory_classes)+os.pathsep+cp,'ProtocolCarrierCounterInventory',str(RUN/'jacoco.exec'),str(component),*sorted(NAMES)])]:
        stage=runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit']==0 and not stage['timedOut']
    counter_inventory={}
    for line in (SLOT/'counter-inventory.stdout').read_text().splitlines():
        parts=line.split('\t')
        if parts[0]=='INVENTORY':
            assert parts[1] not in counter_inventory
            counter_inventory[parts[1]]=dict(crc64=parts[2],probePresent=parts[3]=='true',counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in parts[4:]})
    assert set(counter_inventory)==NAMES and len(NAMES)==11
    METADATA={name for name,row in counter_inventory.items() if sum(row['counters']['CLASS'].values())==0}
    assert TRUE_NO_CODE<=METADATA<=TRUE_NO_CODE|GENERATED_RECORD_CANDIDATES
    assert all(all(v==dict(missed=0,covered=0) for v in counter_inventory[name]['counters'].values()) for name in METADATA)
    EXECUTABLE=NAMES-METADATA
    metadata_kinds={name:('NO_CODE' if name in TRUE_NO_CODE else 'GENERATED_RECORD_CODE') for name in METADATA}
`;
once("    jdk=runner.TC/'jdk-25.0.4/bin';stages=[]\n", "    jdk=runner.TC/'jdk-25.0.4/bin';stages=[]\n" + inventory);
once("and len(metadata)==0 and all(set(r['counters'])", "and len(metadata)==len(METADATA) and all(set(r['counters'])");
once("    kinds=['LINE','METHOD','CLASS','BRANCH']", String.raw`    assert all(rows[name]['counters']==counter_inventory[name]['counters'] and rows[name]['crc64']==counter_inventory[name]['crc64'] for name in EXECUTABLE)
    assert data.sha(inventory_tool.read_bytes())==inventory_pin
    kinds=['LINE','METHOD','CLASS','BRANCH']`);
once("targetSourceUnits=69", "targetSourceUnits=7");
once("namedTypeFixtureSha256='9529fce86672b27a435665331648110521be6f59c5fe3fe5ca516df5234c7a76',", "counterInventory=counter_inventory,metadataKinds=metadata_kinds,inventoryToolSourceSha256=inventory_pin,inventoryToolClassSha256=data.sha((inventory_classes/'ProtocolCarrierCounterInventory.class').read_bytes()),");
once("metadataKind='NONE'", "metadataKind='TRUE_INTERFACES_AND_OPTIONAL_STANDARD_GENERATED_RECORD_FILTERS'");
once("naturalZeroBranchSourcePrograms=sum(v['branchNaturallyZero'] and v['threeCounter100'] for v in units.values()),incompleteSourcePrograms=sum(not(v['four100'] or v['branchNaturallyZero'] and v['threeCounter100']) for v in units.values())", "naturalZeroBranchSourcePrograms=sum(v['branchNaturallyZero'] and v['threeCounter100'] for v in units.values()),noCodeSourcePrograms=sum(v['metadataOnly'] for v in units.values()),incompleteSourcePrograms=sum(not(v['four100'] or v['metadataOnly'] or v['branchNaturallyZero'] and v['threeCounter100']) for v in units.values())");
assert.equal(source.split("    expected_owners=").length - 1, 1);
assert.equal(source.split("def main():").length - 1, 1);
assert(source.includes("name.split('$',1)[0]"));
assert(!source.includes("targetSourceUnits=69"));
const target = "/home/mini/codex/project1/work/pgpt-foundation/tools/quality/pg14862_protocol_carrier_seven_existing_post.py";
process.stdout.write("*** Begin Patch\n*** Add File: " + target + "\n"
    + source.trimEnd().split("\n").map(line => "+" + line).join("\n") + "\n*** End Patch\n");
