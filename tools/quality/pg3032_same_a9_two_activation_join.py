"""Same-a9 first/warm activation join; qualified capsules only, no guest operation."""
import inspect
import pg2390_same_source_native_join as previous

SOURCE = 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
SLOT = 'pg3032-same-a9-two-activation-join-v1'
MANIFESTS = ['43ac98d699d294a126cf48780b4b27ee89f9dde4dde99126daa56ad3de9c5b4f', '53be6798d137f3d5297451da9f066c2124854335b10db28ff111461d1d9f571c']


def payload():
    raw = previous.payload()
    replacements = [('PG2390', 'PG3032'), ('PG2284-native-v1', 'PG2934-native-v1'), ('PG2384-native-v1', 'PG3030-native-v1'), ('PG2228', 'PG2930'), ('PG2300', 'PG3026'), ('3635', '3685'), (previous.SOURCE, SOURCE)]
    for a, b in replacements:
        raw = raw.replace(a, b)
    start = raw.index('MANIFESTS=')
    end = raw.index('\n', start)
    raw = raw[:start] + 'MANIFESTS=' + repr(MANIFESTS) + raw[end:]
    # Compare every non-directory entry, including debug/class and META/resource bytes.
    raw = raw.replace("if n.endswith('.class')", "if not n.endswith('/')")
    raw = raw.replace('main_count=0', 'main_count=0;resource_count=0')
    raw = raw.replace('main_count+=len(images[1]);', "main_count+=sum(n.endswith('.class')for n in images[1]);")
    raw = raw.replace('require(images[0]==images[1]);', "require(images[0]==images[1]);resource_count+=sum(not n.endswith('.class')for n in images[1]);")
    raw = raw.replace('require(main_count==1643)', 'require(main_count==1643 and resource_count==79)')
    raw = raw.replace("'mainClassesIdentical':main_count", "'mainClassesIdentical':main_count,'allResourceMetaMembersIdentical':resource_count")
    compile(raw, '<same a9 two activation all-member join>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.main)
    raw = raw.replace('pg2284-current-signed-native-qualified-v1', 'pg2934-format-fixed-same-native-qualified-v1').replace('pg2384-current-resume-native-qualified-v1', 'pg3030-current-resume-native-qualified-v1').replace('PG2390', 'PG3032')
    ns = {**previous.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<qualified two a9 capsules only>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
