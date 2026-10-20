"""Collect Main-only private monitor symbol/reference facts; never run Production code."""
import datetime
import json
import os
import shutil
import subprocess
from pg5922_current_catch_facts import inputs, SOURCE
from pg5540_snapshot_scratch_selected import ROOT, TC, sha
from source_private_monitor_inventory_test import facts

W = ROOT.parent/'pgpt-runs/PG379'


def main():
    snapshot, classpath, identity = inputs()
    helper = ROOT/'tools/quality/SourcePrivateMonitorInventory.java'
    fixture = ROOT/'tools/quality/source_private_monitor_inventory_test.py'
    helper_sha, fixture_sha = sha(helper), sha(fixture)
    os.umask(0o077); out = W/'pg5932-private-monitor-facts-v3'; out.mkdir(mode=0o700)
    classes = out/'toolclasses'; classes.mkdir()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    commands = [['python3', '-B', '-m', 'unittest', 'source_private_monitor_inventory_test'],
                [str(TC/'jdk-25.0.4/bin/javac'), '--release', '25', '-Xlint:all', '-Werror', '-d', str(classes), str(helper)]]
    exits = []
    for i, command in enumerate(commands):
        with (out/('phase-'+str(i)+'.private.log')).open('xb') as f:
            result = subprocess.run(command, stdout=f, stderr=subprocess.STDOUT, timeout=60)
            exits.append(result.returncode)
        if exits[-1]:
            raise ValueError('independent private monitor fixture/compile0 required')
    mirror = out/'input'; mirror.mkdir()
    for name in identity['sourceHashes']:
        target = mirror/name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(snapshot/name, target)
    if {p.relative_to(mirror).as_posix(): sha(p) for p in mirror.rglob('*.java')} != identity['sourceHashes']:
        raise ValueError('all851 immutable Main-only inputs')
    command = [str(TC/'jdk-25.0.4/bin/java'), '-Xmx1536m', '-cp', str(classes), 'SourcePrivateMonitorInventory', str(mirror), classpath]
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    with (out/'typed.private.log').open('x') as f:
        f.write(result.stdout+result.stderr); f.flush(); os.fsync(f.fileno())
    if result.returncode:
        raise ValueError('all current private monitor symbols must resolve; preserve original failure')
    value = facts(result.stdout)
    if any(r['path'] not in identity['sourceHashes'] for rows in value.values() for r in rows) or inputs() != (snapshot, classpath, identity) or sha(helper) != helper_sha or sha(fixture) != fixture_sha:
        raise ValueError('all851/1666 source/type/helper inputs fixed')
    manifest = dict(actualExit=0, source=SOURCE, startedUTC=started, completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    identity=identity, helperSha256=helper_sha, fixtureSha256=fixture_sha, fixtureExit=exits[0], compileExit=exits[1],
                    commands=commands+[command], facts=value, factsOnlyNotApplicabilityOrPgAcceptance=True,
                    productionCodeChanged=False, testExecutionsIssued=0, ptAlternativeCompleted=0, F03Accepted=False, formalAccepted=False, vmActions=0)
    with (out/'manifest.safe.json').open('x') as f:
        json.dump(manifest, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=SOURCE, privateInlineFinalObjectFields=len(value['fields']),
                         eligibleFields=sum(r['eligible'] for r in value['fields']), monitorBlocks=len(value['blocks']),
                         sourceOwners=len({r['path'] for r in value['blocks']}), manifestSha256=sha(out/'manifest.safe.json'),
                         productionCodeChanged=False, F03Accepted=False)))


if __name__ == '__main__':
    main()
