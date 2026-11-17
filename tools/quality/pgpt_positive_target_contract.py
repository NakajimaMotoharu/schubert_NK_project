"""BUG3208/YKT2669: require probes for actual Code, retain all natural NoCode targets."""

def validate_positive_targets(targets, inventory, positive):
    if (not isinstance(targets, list) or not targets or
            any(not isinstance(n, str) or not n for n in targets) or
            len(set(targets)) != len(targets) or not isinstance(inventory, dict) or
            not isinstance(positive, (set, frozenset))):
        raise ValueError('explicit unique target names, metadata and positive set required')
    executable, no_code = set(), set()
    for name in targets:
        entry = inventory.get(name)
        if not isinstance(entry, dict) or not isinstance(entry.get('methods'), list):
            raise ValueError('every target needs bound classfile method metadata')
        states = []
        for method in entry['methods']:
            if not isinstance(method, dict) or type(method.get('hasCode')) is not bool:
                raise ValueError('explicit boolean Code presence required')
            states.append(method['hasCode'])
        (executable if any(states) else no_code).add(name)
    if not executable <= positive:
        raise ValueError('missing positive executable target')
    if no_code & positive:
        raise ValueError('positive probes contradict natural NoCode metadata')
    return dict(executableTargets=sorted(executable), naturalNoCodeTargets=sorted(no_code),
                measurementTargetsPreserved=list(targets), coverageExclusions=[])
