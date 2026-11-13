"""Metadata-only, explicit unexecuted Guard type; never manufactures a probe."""
from pathlib import Path
import ast,json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'PMO/pgpt-completion-stage-20261102';c=json.loads((B/'input/2173_guard_unexecuted_mode_start.json').read_text());state=json.loads((S/'checkpoint.json').read_text());assert state['ordinaryActiveGroup']==c['groupId'] and state['ordinaryGroupNotYetClosed']
p=R/'tools/quality/pgpt_guard_signature.py';s=p.read_text();assert "option = c.get('guardTypeOnly')" not in s
add='''def type_only(c):
    """Opt-in for one fully reviewed JDBC read Test, retaining every Guard miss."""
    option = c.get('guardTypeOnly')
    if option is None:
        return None
    require(c.get('reviewedGuardSignature') is not None and isinstance(option, dict) and
            set(option) == {'sourceClosure'}, 'explicit witnessed type-only dependency')
    pin = option['sourceClosure']
    require(isinstance(pin, dict) and set(pin) == {'path', 'sha256'} and
            re.fullmatch('[0-9a-f]{64}', pin['sha256']) and
            pin['path'].startswith('evidence/01_PT/018_NK-OPS-001/evidence/') and
            pin['path'].endswith('/manifest.json') and
            pin in c.get('closureProofs', []), 'explicit type-only source proof pin')
    expected = {'ExpiryAuditResourceFailureTest.java', 'JdbcResourceCases.java'}
    require({Path(t['path']).name for t in c['testSources']} == expected and
            len(c['testSources']) == 2 and
            sorted(t['tests'] for t in c['testSources']) in [[0, 3], [0, 4]],
            'only whole reviewed Expiry resource Test and original helper')
    require(not c.get('sdkJars') and not c.get('systemProperties') and
            c.get('reviewedArtemisSdk') is None and not c.get('reviewedReflection'),
            'no backend SDK, reflection or property execution permission')
    return pin


def checked_type_only(c):
    pin = type_only(c)
    if pin is None:
        return
    path = R / pin['path']
    require(digest(path) == pin['sha256'], 'type-only source proof hash')
    witness = json.loads(path.read_text())
    require(witness.get('schema') == 'PGPT_GUARD_TYPE_ONLY_SOURCE_V1' and
            witness.get('actualExit') == 0 and witness.get('guardDefaultCodeCalls') == 0 and
            witness.get('noGuardInstancesOrOverrides') is True and
            witness.get('allGuardCountersRetained') is True,
            'reviewed non-executed type contract')
    expected_main = {'ExpiryAuditRepository', 'RunReferenceRepository', 'RunReferences',
                     'BatchRun', 'BatchStepAttempt', 'BatchStep', 'BatchStepResult',
                     'SuccessRunLookup', 'JdbcResourceFailures', 'BatchRepositoryException',
                     'StorageIoException'}
    require(len(c['mainSources']) == 11 and
            {Path(n).stem for n in c['mainSources']} == expected_main,
            'exact previously reviewed Main closure')
    require(witness.get('mainInputHashes') == {n: digest(R / n) for n in c['mainSources']} and
            witness.get('wholeTestHashes') == {t['path']: digest(R / t['path']) for t in c['testSources']},
            'all current whole source bytes reviewed and pinned')
    for item in c['testSources']:
        text = (R / item['path']).read_text()
        require(not re.search(r'\\b(?:Guard|MaintenanceOwnerFrame|ClassLoader|Class|MethodHandles)\\b|'
                              r'\\.(?:successful|stage|finish|forName|getDeclaredMethod|invoke)\\s*\\(', text),
                'no Guard instance, default call, reflection or other repository phase')
    text = (R / SOURCE).read_text()
    start = text.index('  public interface Guard {')
    end = text.index('\\n  private static final String[] KEYS', start)
    require(text[start:end].count('default ') == 2 and
            'static ' not in text[start:end] and '{\\n    long remainingNanos()' in text[start:end],
            'unchanged interface has no initializer, only two unexecuted defaults')


'''
s=s.replace('def validate_witness(c, witness, pre, current_source_sha):',add+'def validate_witness(c, witness, pre, current_source_sha):');s=s.replace("    for name in c['mainSources'] + [t['path'] for t in c['testSources']]:\n", "    checked_type_only(c)\n    for name in c['mainSources'] + [t['path'] for t in c['testSources']]:\n");s=s.replace("    option = c.get('reviewedGuardSignature')\n", "    type_only(c)\n    option = c.get('reviewedGuardSignature')\n",1);ast.parse(s);p.write_text(s)
p=R/'tools/quality/pgpt_closed_host_post.py';s=p.read_text();old="    if signature is not None:\n        require(guard_name in observed, 'fresh real Guard execution required')";assert s.count(old)==1;s=s.replace(old,"    type_only_guard = signature is not None and c.get('guardTypeOnly') is not None\n    if signature is not None:\n        if type_only_guard:\n            require(guard_name not in probes, 'type-only Guard must have no executed probe')\n            require(method_counts[guard_name] == 2, 'two real default methods, no initializer')\n        else:\n            require(guard_name in observed, 'fresh real Guard execution required')")
s=s.replace("    require(real - observed <= no_code and observed <= real, 'class init and exec membership')", "    legitimate_unexecuted_interface = {guard_name} if type_only_guard else set()\n    require(real - observed <= no_code | legitimate_unexecuted_interface and observed <= real, 'class init and exec membership')")
anchor="    targets = {n: counters(classes[n]) for n in c['targetClasses']}";assert s.count(anchor)==1;s=s.replace(anchor,"    if type_only_guard:\n        require(all(row['covered'] == 0 for row in counters(classes[guard_name]).values()),\n                'all real unexecuted Guard counters remain fully missed')\n"+anchor);s=s.replace("    result['guardSignature'] = signature", "    result['guardSignature'] = signature\n    result['guardExecutionMode'] = 'TYPE_ONLY_ALL_COUNTERS_MISSED' if type_only_guard else ('FRESH_POSITIVE_REQUIRED' if signature is not None else None)");ast.parse(s);p.write_text(s);print('metadata-only feature edited; no Product compile/run/class access')
