"""Validate an append-only explanation correction; never import or execute a PT driver."""
import ast
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_assignments(path):
    values = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    values[target.id] = value
    return values


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(root, correction):
    require(correction['productExecution'] is False, 'metadata only')
    require(len(correction['rows']) == 7, 'seven original runs, six configurations')
    seen = set()
    configs = set()
    for row in correction['rows']:
        driver = root / row['driver']
        config = root / row['config']
        manifest = root / row['manifest']
        require(sha(driver) == row['driverSha256'], 'original driver pin')
        require(sha(config) == row['configSha256'], 'original config pin')
        require(sha(manifest) == row['manifestSha256'], 'original result pin')
        values = literal_assignments(driver)
        actual = json.loads(manifest.read_text())
        dependencies = json.loads(config.read_text())
        require(values['CFG'] == row['config'], 'config binding')
        require(values['expectedTests'] == row['expectedTests'] == actual['tests'], 'test count')
        require(values['expectedSnapshots'] == row['expectedSnapshots'] == actual['snapshotCount'], 'DOM count')
        require(values['tag'] == row['tag'], 'Test ID prefix')
        require(actual['source'] == row['runtimeSource'], 'preserve original runtime source')
        require(actual['inputHashes'][row['config']] == row['configSha256'], 'original input pin')
        require(actual['inputHashes'][row['driver']] == row['driverSha256'], 'original observer pin')
        require(dependencies['resources'] == row['resources'], 'resource scope unchanged')
        require(actual['actualExit'] == 0 and all(actual[k] == 0 for k in ['failures', 'errors', 'skipped', 'aborted']), 'saved result counters')
        require(len([name for name in actual['files'] if name.startswith('output/')]) == row['expectedSnapshots'], 'saved output count')
        for name, expected in actual['files'].items():
            require(sha(manifest.parent / name) == expected, 'saved public file pin')
        require(row['manifest'] not in seen, 'no double result')
        seen.add(row['manifest'])
        configs.add(row['config'])
    require(len(configs) == 6, 'six affected configurations')
    inventory = {str(p.relative_to(root)): sha(p) for p in (root / correction['configDirectory']).glob('*dependencies.json')}
    classified = {row['path']: row['sha256'] for row in correction['inventory']}
    require(inventory == classified and len(classified) == len(correction['inventory']), 'complete bounded inventory')
    require({row['path'] for row in correction['inventory'] if row['status'] == 'EXPLANATION_CORRECTED_APPEND_ONLY'} == configs, 'all affected configurations')
    return {'runs': len(seen), 'affectedConfigurations': len(configs), 'inventory': len(inventory), 'newProductTests': 0, 'sourceQualificationsTransferred': 0}


def check_future_contract(config, tests, snapshots, tag):
    """Use before a new resource PT, without revising a frozen historical input."""
    require((config['expectedTests'], config['expectedSnapshots'], config['tag']) == (tests, snapshots, tag), 'future config disagrees with driver')


if __name__ == '__main__':
    root = Path.cwd()
    path = root / 'evidence/01_PT/016_NK-WEB-002/input/037_resource_metadata_corrections.json'
    print(json.dumps(validate(root, json.loads(path.read_text())), ensure_ascii=False))
