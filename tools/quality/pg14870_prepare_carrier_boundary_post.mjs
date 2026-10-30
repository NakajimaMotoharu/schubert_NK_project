import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {replaceExactlyOnce} from './literal_template_replace_v1.mjs';
let source=readFileSync('tools/quality/pg14862_protocol_carrier_seven_existing_post.py','utf8');
assert.equal(createHash('sha256').update(source).digest('hex'),'5e7c471e02edc27e9945879516275bc64d4af5f52b78bb3b5f6533e0fe1b112e');
const changes=[
 ['Saved original31 only: seven carrier Source closures, true interfaces versus standard filtered records.','New boundary6 only: whole carrier closures, no prior exec union or original31 replay.'],
 ['import pg14360_protocol_semantic_whole_thirty_one_pt as original','import pg14868_protocol_carrier_boundary_six_pt as original'],
 ['4123691e8775684b13142b4b9c319bca82956c008163c63793dedb5b4de7ebd2','7dce0ee6ffd042a498ae7bfcbf20d9f2d5a0ce0f82d3e9e8ed716e6211a0bd55'],
 ["RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14360-protocol-semantic-whole-thirty-one-pt-v1'","RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14868-protocol-carrier-boundary-six-pt-v1'"],
 ["OUT=data.BASE/'PG14862-protocol-carrier-seven-existing-post-v1'","OUT=data.BASE/'PG14870-protocol-carrier-boundary-six-post-v1'"],
 ["SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14862-protocol-carrier-seven-existing-post-v1'","SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14870-protocol-carrier-boundary-six-post-v1'"],
 ['TOTAL=31','TOTAL=6'],
 ["data.BASE/'PG14360-protocol-semantic-whole-thirty-one-pt-v1/manifest.json'","data.BASE/'PG14868-protocol-carrier-boundary-six-pt-v1/manifest.json'"],
 ["and prior['execSha256']==raw['execSha256']","and prior['execSha256']!=raw['execSha256']"],
 ["{(v['classname'],v['name']) for v in raw['cases']}<={(v['classname'],v['name']) for v in registry['cases']}","not {(v['classname'],v['name']) for v in raw['cases']}&{(v['classname'],v['name']) for v in registry['cases']}"],
 ["tests=TOTAL,suites=7,failures=0","tests=TOTAL,suites=1,failures=0"],
 ["newTestIds=0,newAccepted=0","newTestIds=6,newAccepted=0"],
 ["currentSourceExistingExecReanalyzed=True,originalTestsCountedElsewhere=True,newProductExecutions=0,newUniqueMethods=0,originalPostReference=dict(name='PG14362-protocol-semantic-whole-thirty-one-post-v1',sha256='f03bb6730c2491b463c9400972de775f65a389c54a4e65d24c8a6aa1d3fef177')","currentSourceExistingExecReanalyzed=False,originalTestsCountedElsewhere=False,newProductExecutions=1,newUniqueMethods=6,previousSourceBaselineReference=dict(name='PG14862-protocol-carrier-seven-existing-post-v1',sha256='33a0eaa5881826498d6b9b22d4b6436e50445dedbc713ffc5c056092611b1738')"],
 ['actualExit=0,tests=TOTAL,suites=7,sourcePrograms','actualExit=0,tests=TOTAL,suites=1,sourcePrograms']
];
for(const [from,to] of changes)source=replaceExactlyOnce(source,from,to);
const oracle="[*original.TESTS.values(),original.ROOT/'IndependentNamedFieldOracle.java']";
assert.equal(source.split(oracle).length-1,2);
source=source.split(oracle).join('list(original.TESTS.values())');
assert.equal(source.split('expected_owners=').length-1,1);
assert.equal(source.split('def main():').length-1,1);
assert.ok(source.includes("name.split('$',1)[0]"));
process.stdout.write('*** Begin Patch\n*** Add File: /home/mini/codex/project1/work/pgpt-foundation/tools/quality/pg14870_protocol_carrier_boundary_post.py\n'+source.trimEnd().split('\n').map(line=>'+'+line).join('\n')+'\n*** End Patch\n');
