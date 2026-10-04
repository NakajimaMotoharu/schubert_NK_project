"""Independent fixed-cohort preflight. No native operation or private payload copying."""
import pathlib, hashlib
ROOT=pathlib.Path(__file__).resolve().parent
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
watch=WORK/'pg460-parent-watch-private-v1.jsonl'
assert hashlib.sha256(watch.read_bytes()).hexdigest()=='89df0f075188e957492d7dd0c0fa2504a43528c52c290c018d306a6a4d3a4c30'
sources={n:(ROOT/n).read_text() for n in ['Pg461CapturedPeers.java','Pg461CapturedPeersTest.java','Pg461OwnedIsolation.java','Pg461Known30PairRecovery.java','Pg461Known30PairRecoveryTest.java']}
for name,s in sources.items():
    for stale in ['089998999b9d95fc7d093e3bb6d7403f78e22882a3883c8ff0fd3b8c6d9e0e65','57c21415bf71b170dec3e5af719f795f38c1a186f2c71c360cb78aaeeff68e7d','314305','456625','458728','59028b20d8e5400abe86398d16e57645','520f6a223a2f48f8a4a1cae019e23364','c33f5fdfd402482b93b825922115a225','==281','all281','==13']:
        assert stale not in s,(name,'stale fixed binding')
for name in ['Pg461OwnedIsolation.java','Pg461Known30PairRecovery.java']:
    s=sources[name]
    for value in ['271136af03ae47e3ba9f398e2e2a24b0','25020aa0-7b69-4554-be47-ea69588da569','rows.size()==291']:
        assert value in s,(name,'missing fixed binding')
assert '89df0f075188e957492d7dd0c0fa2504a43528c52c290c018d306a6a4d3a4c30' in sources['Pg461OwnedIsolation.java']
assert '097c5246b98738659ebfbf525cbeedc99213f3cbf9736767dd2dc4cb18f30299' in sources['Pg461Known30PairRecovery.java']
assert 'expected.size()==17' in sources['Pg461Known30PairRecovery.java']
assert 'actual.size()==17' in sources['Pg461Known30PairRecoveryTest.java']
for value in ['9365225','9437302','9438438','471458','613477','615605','8e97eb9138828010926cd47fd10868d8a2d54f11']:
    assert value in sources['Pg461CapturedPeers.java']
for old in ['1eecb7b9-1e98-478f-9084-201422b31bff','d536cf5a-f5a8-4dd9-8679-3488fab17fdf','e8cce97a-163b-4814-b435-8fc26466e550']:
    assert old in sources['Pg461Known30PairRecovery.java'] and old in sources['Pg461Known30PairRecoveryTest.java']
code=(ROOT/'Pg461CodeOnlyDeployment.java').read_text()
assert 'rows.size()==291' in code
assert 'before.epoch().toString().equals("25020aa0-7b69-4554-be47-ea69588da569")' in code
assert 'static final Path OLD=Path.of("/opt/schubert-nk/releases/0.1.0-PG459")' in code
assert 'static final Path NEXT=Path.of("/opt/schubert-nk/releases/0.1.0-PG461")' in code
assert 'OLD_SOURCE="8e97eb9138828010926cd47fd10868d8a2d54f11"' in code
assert 'OLD_DIGEST="88a6504f93782c65e2328bd719db4133bdc2b3457d0495c9e5887d084fd38311"' in code
assert '25020aa0-7b69-4554-be47-ea69588da569.permit' not in code
print('PG461_COHORT_BINDINGS_PASS independentPins=true nativeMutation=false productionPt0=true')
