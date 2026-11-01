import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { replaceProfileLiterals } from "./literal_profile_replace_v2.mjs";
const digest = value => createHash("sha256").update(value).digest("hex");
assert.equal(process.version, "v24.19.0");
const template = readFileSync(new URL("./pg18250_session_technical_eight_pt.py", import.meta.url), "utf8");
assert.equal(digest(template), "acd4616abe0c19b26fb62b5e633e1f272e70c458bb0d3d4434c5dd7fb5e6d94b");
assert.equal(digest(readFileSync(new URL("./literal_profile_replace_v2.mjs", import.meta.url))), "3370b22463c9e46781511d0de63e216c8d207f425a4fe3cf8c91d4bc7aa08df2");
const mapping = {"SessionTechnicalValueContractTest":"WebTerminalFlagContractTest","0693d069c344dd8201c15c03cec259ab4e42f0a7ad42adbf178528dd8b44bb8b":"96e51d13830a50e2837a1bfdb6e789392927c2952ae9b265be47ef9e485c70d0","PG18250-SESSION-TECHNICAL8":"PG18300-WEB-TERMINAL-FLAG4","PG18249-session-technical-review-v1":"PG18299-web-terminal-flag-review-v1","PG18238-current2937-media-display-registry-v1":"PG18278-current2955-revoke-values-registry-v1","0a8a2f43c4eed352e40b73003297244475c34bafe48df79f1899b7c818ee0358":"1f8ddb95b0f15c064e702f6ace5023309575a4ddb3796bdb4c8fec1cda26ade3","independentNewQualityTests=8":"independentNewQualityTests=4","pureSessionTechnicalValuesOnly=True,syntheticEncryptedPayloadMetadataOnly=True,actualPayloadEncryptionOrDecryption=False":"pureCapturedTerminalFlagOnly=True,selfOwnedExecutorFixtureInvoked=True,declaredOwnPlatformThreadMaximum=4","pg18250-session-technical-eight-pt-v1":"pg18300-web-terminal-flag-four-pt-v1","PG18250-session-technical-eight-pt-v1":"PG18300-web-terminal-flag-four-pt-v1","SessionTechnicalEightCurrentJunitLauncher":"WebTerminalFlagFourCurrentJunitLauncher","publicFixedUuidFixtureOnly=True":"publicFixedUuidFixtureOnly=False","declaredOwnThreadCount=0":"declaredOwnThreadCount=None","declaredOwnExecutorInstances=0":"declaredOwnExecutorInstances=1","declaredOwnTaskCount=0":"declaredOwnTaskCount=64","'Executors.',":""};
mapping[template.match(/^MAIN_UNITS=.*$/m)[0]] = "MAIN_UNITS="+"{\"dev/codex/schubert/nk/web/bootstrap/WebRuntimeFailureSignal\":{\"module\":\"web\",\"name\":\"dev/codex/schubert/nk/web/bootstrap/WebRuntimeFailureSignal\",\"sha256\":\"9a90ff25dd5bd987b3524da8cff9e37511d82cef6901256e948afa5609822269\"}}";
mapping[template.match(/^PUBLIC_READS=.*$/m)[0]] = "PUBLIC_READS={}";
mapping[template.match(/^COUNTS=.*$/m)[0]] = "COUNTS={'WebTerminalFlagContractTest':4}";
// Counts come from the exact frozen template via an independent non-regex scan.
const counts = Object.fromEntries(Object.keys(mapping).map(key => [key, 0]));
for (let pos=0; pos<template.length;) {
  let selected;
  for (const key of Object.keys(mapping)) {
    if (template.startsWith(key,pos) && (!selected || key.length>selected.length)) selected=key;
  }
  if (selected) { counts[selected]++; pos+=selected.length; }
  else pos++;
}
assert.ok(Object.values(counts).every(count=>count>0));
const entries = Object.entries(mapping).map(([key,value]) => [key,value,counts[key]]);
const result = replaceProfileLiterals(template,entries);
assert.ok(result.text.includes("COUNTS={'WebTerminalFlagContractTest':4}"));
assert.ok(!result.text.includes("SessionTechnicalValueContractTest"));
assert.ok(result.text.includes("declaredOwnExecutorInstances=1"));
process.stdout.write(JSON.stringify({
  text:result.text,
  receipt:{
    source:"6b53efeec87f3ec36a840dd8e7759656cb4aee5c",actualExit:0,
    generatorSha256:digest(readFileSync(new URL(import.meta.url))),
    templateSha256:digest(template),helperSha256:"3370b22463c9e46781511d0de63e216c8d207f425a4fe3cf8c91d4bc7aa08df2",
    generatedSha256:digest(result.text),originalOccurrenceCounts:counts,
    generatedCodeExecuted:false,productTestsExecuted:0,actualVmActions:0,actualDatabaseActions:0,actualNetworkActions:0,
    normalOnlyTrueWorkerFixture:true,actualNodeArgv:process.argv,runtimeVersion:process.version
  }
})+"\n");
