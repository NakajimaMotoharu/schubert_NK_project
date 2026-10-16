"""SSC293 data-only full-FD continuity; only independently socket-bound DB pool may roll."""
import re
import stat

ROLES = {'schubert_app': ('schubert-nk-api.service', 'schubert-nk-api', 2, 8),
         'schubert_web_session': ('schubert-nk-web.service', 'schubert-nk-web', 1, 2)}


def require(value):
    if value is not True:
        raise ValueError('current complete descriptor capability proof refused')


def captured_inodes(fds):
    result = set()
    for fd in fds.values():
        match = re.fullmatch(r'socket:\[([1-9][0-9]*)\]', fd['target'])
        if match:
            require(fd['metadata'][1] == int(match[1]) and stat.S_ISSOCK(fd['metadata'][4]))
            result.add(match[1])
    return result


def bind(value, table, server_inodes, tcp_pair, endpoint, completed=frozenset(), owned_backend=None):
    require(type(value) is dict and type(table) is list and type(server_inodes) is dict)
    result = {}; counts = {role: 0 for role in ROLES}; used_inodes = set(); management = 0
    for peer in value['database']['peers']:
        if peer['user'] not in ROLES:
            require(owned_backend is not None and peer['pid'] == owned_backend
                    and peer['user'] == 'schubert_batch' and peer['application'] == 'PG286-original-profile')
            management += 1; require(management == 1)
            continue
        unit, application, unused_low, unused_high = ROLES[peer['user']]
        require(unit not in completed and peer['application'] == application and peer['address'] == '127.0.0.1')
        actor = value['actors'][unit]; detail = value['detailedActors'][unit]
        require(detail['identity'] == actor and peer['pid'] in server_inodes)
        fds = detail['fds']; client_inodes = captured_inodes(fds)
        tcp_pair(table, peer['port'], client_inodes, server_inodes[peer['pid']])
        matches = [r for r in table if endpoint(r[1]) == ('127.0.0.1', peer['port'])
                   and endpoint(r[2]) == ('127.0.0.1', 5432) and r[3] == '01' and r[9] in client_inodes]
        require(len(matches) == 1)
        inode = matches[0][9]; require(inode not in used_inodes); used_inodes.add(inode)
        aliases = [fd for fd, record in fds.items() if record['target'] == 'socket:[' + inode + ']']
        require(len(aliases) == 1)
        fd = aliases[0]; record = fds[fd]; metadata = record['metadata']
        require(len(metadata) == 9 and all(type(n) is int and n >= 0 for n in metadata)
                and metadata[2:4] == [detail['nss']['uid'], detail['nss']['gid']]
                and metadata[4:7] == [stat.S_IFSOCK | 0o777, 1, 0]
                and record['flags'] == '04002' and record['mountId'] == '12')
        require(fd not in result.setdefault(unit, {}))
        result[unit][fd] = {'peer': peer, 'client': matches[0]}; counts[peer['user']] += 1
    for role, (unit, unused_application, low, high) in ROLES.items():
        require(counts[role] == 0 if unit in completed else low <= counts[role] <= high)
    require(management == (1 if owned_backend is not None else 0))
    return result


def same_details(before, after, before_pool, after_pool):
    require(type(before) is dict and type(after) is dict and set(before) == set(after))
    for unit, old in before.items():
        now = after[unit]
        require(set(old) == set(now) == {'identity', 'authority', 'nss', 'children', 'fds'})
        require(all(old[key] == now[key] for key in ['identity', 'authority', 'nss', 'children']))
        old_pool = before_pool.get(unit, {}); new_pool = after_pool.get(unit, {})
        require(set(old_pool) <= set(old['fds']) and set(new_pool) <= set(now['fds']))
        require({fd: record for fd, record in old['fds'].items() if fd not in old_pool}
                == {fd: record for fd, record in now['fds'].items() if fd not in new_pool})
    return True
