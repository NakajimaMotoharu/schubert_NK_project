"""Final candidate-byte ABBA with cross-process canonical value digests, no authority."""
import inspect
import pg4404_shared_manager_candidate_cost as previous
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4406-verified-shared-manager-cost-v1'


def payload():
    raw = previous.payload()
    raw = once(raw, 'SLOT=' + repr(previous.SLOT), 'SLOT=' + repr(SLOT))
    old = previous.previous.java()
    new = once(old, 'byte[] expected = read.read();',
               'byte[] expected = read.read();\n    String expectedSha256 = java.util.HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(expected));')
    new = once(new, '+",\\\"syscr\\\":"+(after.get("syscr")-before.get("syscr"))+"}";',
               '+",\\\"syscr\\\":"+(after.get("syscr")-before.get("syscr"))+",\\\"observedValueSha256\\\":\\\""+expectedSha256+"\\\"}";')
    raw = once(raw, 'JAVA=' + repr(old), 'JAVA=' + repr(new))
    raw = once(raw, 'assert manifest.read_bytes()==before\nvalue=',
               "assert len({r['result']['samples'][0]['observedValueSha256']for r in results})==1\nassert manifest.read_bytes()==before\nvalue=")
    return once(raw, "'comparisons':results}", "'allOriginalCandidateSevenFieldValuesEqual':True,'comparisons':results}")


def main():
    transport = previous.previous.previous.previous
    ns = {**vars(transport), 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(transport.main), '<same canonical values fixed ABBA>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    main()
