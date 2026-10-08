"""BUG857 explicit known test-only difference; no general src waiver."""
from pg561_current_native_counter import same_production_paths,KNOWN_TEST
assert same_production_paths([])
assert same_production_paths([KNOWN_TEST])
for invalid in (None,{},'',True,[None],[KNOWN_TEST]*2,['pom.xml'],['src/schubert-nk-batch/src/main/java/Changed.java'],['src/schubert-nk-web/src/main/resources/login.html'],['src/schubert-nk-batch/src/test/java/ForeignTest.java']):
 assert not same_production_paths(invalid)
print('PG561_SOURCE_GUARD_ORACLE explicitKnownTestOnly=true unknownMainPomTestNullRejected=true formal0=true')
