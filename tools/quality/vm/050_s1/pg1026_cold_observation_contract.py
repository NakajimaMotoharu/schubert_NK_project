"""SSC244/BUG1010 data-only held inventory and once-TERM contracts.

No entrypoint, Unit operation, mount, DB connection, permit or VM authority.
Callers must authenticate fixed source/boot/pin/approval and continuous exclusion.
HeldInventory proves content/metadata/ACL stability, NOT host filesystem RO.
"""
import hashlib
import os
from pathlib import PurePosixPath
import re
import stat


def metadata(fd):
    s = os.fstat(fd)
    return (s.st_dev, s.st_ino, s.st_uid, s.st_gid, s.st_mode, s.st_nlink,
            s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def attributes(fd):
    return tuple((name, os.getxattr(fd, name)) for name in sorted(os.listxattr(fd)))


class HeldInventory:
    """Anchor every ancestor and signed entry until an explicitly normal close."""

    def __init__(self, root, records, owner):
        if type(owner) is not int or owner < 0 or type(records) is not list or not records:
            raise ValueError('inventory contract refused')
        path = PurePosixPath(root)
        if not path.is_absolute() or '..' in path.parts:
            raise ValueError('absolute inventory root refused')
        self.root = path
        self.owner = owner
        self.records = {}
        for item in records:
            if type(item) is not dict or set(item) != {'path', 'size', 'sha256'}:
                raise ValueError('inventory record refused')
            name = item['path']
            if (type(name) is not str or not name or name == '.' or str(PurePosixPath(name)) != name
                or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts
                or '\\' in name or any(ord(c) < 32 or ord(c) == 127 for c in name)
                or name in self.records or type(item['size']) is not int
                or not 0 <= item['size'] <= 2147483647
                or type(item['sha256']) is not str
                or re.fullmatch('[0-9a-f]{64}', item['sha256']) is None):
                raise ValueError('inventory path/size/hash refused')
            self.records[name] = dict(item)
        self.held = []
        self.closed = False
        self.root_fd = None

    def _hold(self, parent, name, directory):
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        if directory:
            flags |= os.O_DIRECTORY
        fd = os.open(name, flags, dir_fd=parent)
        self.held.append((fd, parent, name, metadata(fd), attributes(fd)))
        m = metadata(fd)
        if (m[2] not in (0, self.owner) or m[4] & 0o022
            or not (stat.S_ISDIR(m[4]) if directory else stat.S_ISREG(m[4]))
            or not directory and m[5] != 1):
            raise ValueError('inventory ownership/type/mode refused')
        return fd

    def open(self):
        if self.held or self.closed:
            raise ValueError('inventory scope reused')
        try:
            fd = self._hold(None, '/', True)
            for component in self.root.parts[1:]:
                fd = self._hold(fd, component, True)
            self.root_fd = fd
            expected_dirs = set()
            for name in self.records:
                expected_dirs.update(str(p) for p in PurePosixPath(name).parents if str(p) != '.')
            found = set()

            def walk(parent, prefix):
                for name in sorted(os.listdir(parent)):
                    relative = prefix + name
                    if relative in expected_dirs:
                        child = self._hold(parent, name, True)
                        walk(child, relative + '/')
                    elif relative in self.records:
                        self._hold(parent, name, False)
                        found.add(relative)
                    else:
                        raise ValueError('unsigned inventory entry refused')
            walk(fd, '')
            if found != set(self.records):
                raise ValueError('inventory entry missing')
            self.capture()
            return self
        except BaseException:
            self.close()
            raise

    def capture(self):
        if self.closed or self.root_fd is None:
            raise ValueError('inventory scope unavailable')
        observed = []
        for fd, parent, name, fixed, acl in self.held:
            current = metadata(fd)
            linked = os.stat(name, dir_fd=parent, follow_symlinks=False)
            identity = (linked.st_dev, linked.st_ino, linked.st_uid, linked.st_gid,
                        linked.st_mode, linked.st_nlink, linked.st_size,
                        linked.st_mtime_ns, linked.st_ctime_ns)
            if current != fixed or identity != fixed or attributes(fd) != acl:
                raise ValueError('inventory metadata/identity/ACL changed')
            digest = None
            if stat.S_ISREG(current[4]):
                h = hashlib.sha256()
                offset = 0
                while offset < current[6]:
                    chunk = os.pread(fd, min(131072, current[6] - offset), offset)
                    if not chunk:
                        raise ValueError('inventory truncated')
                    h.update(chunk)
                    offset += len(chunk)
                digest = h.hexdigest()
                # Match by anchored parent/name, not a second pathname read.
                relative = str(PurePosixPath(os.readlink('/proc/self/fd/' + str(fd))).relative_to(self.root))
                item = self.records[relative]
                if current[6] != item['size'] or digest != item['sha256']:
                    raise ValueError('inventory signed bytes changed')
            if metadata(fd) != fixed or attributes(fd) != acl:
                raise ValueError('inventory changed during read')
            observed.append((name, current, acl, digest))
        return tuple(observed)

    def open_file(self):
        """Pin one separately provisioned file, without claiming parent closure.

        Closed release inventories MUST use open(), not this material-file scope.
        """
        if self.held or self.closed or len(self.records) != 1:
            raise ValueError('single material scope refused')
        name = next(iter(self.records))
        if '/' in name:
            raise ValueError('single material name refused')
        try:
            fd = self._hold(None, '/', True)
            for component in self.root.parts[1:]:
                fd = self._hold(fd, component, True)
            self.root_fd = fd
            self._hold(fd, name, False)
            self.capture()
            return self
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.closed:
            raise ValueError('inventory double close')
        self.closed = True
        failures = []
        for fd, *_ in reversed(self.held):
            try:
                os.close(fd)
            except OSError as failure:
                failures.append(failure)
        if failures:
            raise failures[0]


def all_client_sql(parent_backend):
    if type(parent_backend) is not int or not 0 <= parent_backend < 2147483647 or parent_backend == 1:
        raise ValueError('backend identity refused')
    # The psql observation itself is excluded; every role, including migration or
    # an unknown client role, remains in scope. Dedicated parent is separately attested.
    return ("select count(*)from pg_stat_activity where datname='schubert_nk'"
            "and backend_type='client backend'and pid<>pg_backend_pid()and pid<>"
            + str(parent_backend) + ";")


def fd_alias_records(lines):
    """Normalize only exact fdinfo aliases; kernel cardinality is checked separately."""
    if type(lines) is not list or any(type(line) is not str for line in lines):
        raise ValueError('fdinfo records refused')
    result = []
    for line in lines:
        fields = line.split()
        if (len(fields) != 8 or not fields[0].endswith(':')
            or not fields[0][:-1].isdigit() or fields[1:4] != ['FLOCK', 'ADVISORY', 'WRITE']
            or not fields[4].isdigit() or fields[6:] != ['0', 'EOF']):
            raise ValueError('fdinfo lock refused')
        # Record number is local to a descriptor, not a kernel lock identity.
        canonical = '1: ' + ' '.join(fields[1:])
        if canonical not in result:
            result.append(canonical)
    return result


def free_flocks(lines, lock_metadata):
    if (type(lines) is not list or any(type(line) is not str for line in lines)
        or type(lock_metadata) is not dict
        or set(lock_metadata) != {'maintenance.lock', 'startup-admission.lock'}):
        raise ValueError('free lock contract refused')
    identities = set()
    for m in lock_metadata.values():
        if (type(m) is not list or len(m) != 9 or any(type(x) is not int for x in m)
            or m[2:7] != [0, 0, stat.S_IFREG | 0o600, 1, 0]):
            raise ValueError('free lock metadata refused')
        identity = (os.major(m[0]), os.minor(m[0]), m[1])
        if identity in identities:
            raise ValueError('free lock inode alias refused')
        identities.add(identity)
    for line in lines:
        fields = line.split()
        if len(fields) > 1 and fields[1] == '->':
            fields = [fields[0], *fields[2:]]
        if len(fields) < 2 or fields[1] != 'FLOCK':
            continue
        if len(fields) != 8:
            raise ValueError('free lock record refused')
        parts = fields[5].split(':')
        if len(parts) != 3:
            raise ValueError('free lock address refused')
        identity = (int(parts[0], 16), int(parts[1], 16), int(parts[2]))
        if identity in identities:
            raise ValueError('lock still held or contended')
    return True


def timer_path_classification(raw, console):
    if type(raw) is not str:
        raise ValueError('timer/path listing refused')
    expected = {'Id': 'systemd-ask-password-console.path', 'LoadState': 'loaded',
                'ActiveState': 'active', 'SubState': 'waiting', 'Job': '',
                'Paths': '/run/systemd/ask-password (DirectoryNotEmpty)',
                'Triggers': 'systemd-ask-password-console.service',
                'FragmentPath': '/usr/lib/systemd/system/systemd-ask-password-console.path',
                'DropInPaths': ''}
    result = {}
    for line in raw.splitlines():
        fields = line.split()
        if len(fields) < 4 or fields[0] in result or not fields[0].endswith(('.path', '.timer')):
            raise ValueError('timer/path record refused')
        if fields[0] == expected['Id'] and fields[1:4] == ['loaded', 'active', 'waiting']:
            if type(console) is not dict or console != expected:
                raise ValueError('nonbusiness password-console contract changed')
            result[fields[0]] = 'FIXED_OS_PASSWORD_MONITOR_ONLY'
        elif fields[1:4] == ['loaded', 'inactive', 'dead']:
            result[fields[0]] = 'INACTIVE'
        else:
            raise ValueError('active/unknown timer/path refused')
    return result


def canonical_sum_bytes(records, manifest_hash):
    if (type(records) is not list or not records or type(manifest_hash) is not str
        or re.fullmatch('[0-9a-f]{64}', manifest_hash) is None):
        raise ValueError('checksum contract refused')
    hashes = {'RELEASE-MANIFEST.json': manifest_hash}
    for item in records:
        if type(item) is not dict or set(item) != {'path', 'size', 'sha256'}:
            raise ValueError('checksum record refused')
        name = item['path']
        if (type(name) is not str or not name or name == '.' or not name.isascii()
            or str(PurePosixPath(name)) != name or PurePosixPath(name).is_absolute()
            or '..' in PurePosixPath(name).parts or '\\' in name
            or any(ord(c) < 33 or ord(c) == 127 for c in name)
            or name in hashes or name == 'SHA256SUMS'
            or type(item['size']) is not int or item['size'] < 0
            or type(item['sha256']) is not str or re.fullmatch('[0-9a-f]{64}', item['sha256']) is None):
            raise ValueError('checksum path/hash refused')
        hashes[name] = item['sha256']
    return ''.join(hashes[name] + '  ' + name + '\n' for name in sorted(hashes)).encode('ascii')


def namespace_layout(entries, meta, workers, prepared):
    if (type(entries) is not dict or type(meta) is not dict or type(workers) is not dict
        or set(workers) != {'backup','inspector'} or type(prepared) is not bool):
        raise ValueError('namespace layout contract refused')
    for pair in workers.values():
        if type(pair) is not tuple or len(pair) != 2 or any(type(v) is not int or not 0 < v < 2147483647 for v in pair):
            raise ValueError('namespace worker identity refused')
    names = {'startup','backup-request','cleanup-request','expiry-request','pt-coverage'}
    children = {'parent','cleanup','expiry','root-api','backup','inspector'}
    keys = {'@root','maintenance'} | (names | {'pt-coverage/'+n for n in children} if prepared else set())
    if set(entries) != keys or set(meta) != keys:
        raise ValueError('namespace object set refused')
    for name in keys:
        value = entries[name]
        m = meta[name]
        if (type(value) is not list or any(type(x) is not str for x in value) or len(value) != len(set(value))
            or type(m) is not list or len(m) != 9 or any(type(x) is not int for x in m)):
            raise ValueError('namespace metadata/entries refused')
        expected = {'maintenance.lock','startup-admission.lock','maintenance'} | (names if prepared else set()) if name == '@root' else children if name == 'pt-coverage' else set()
        mode = 0o755 if name == '@root' else 0o711 if name == 'pt-coverage' else 0o700
        owner = workers.get(name.removeprefix('pt-coverage/'), (0,0)) if name.startswith('pt-coverage/') else (0,0)
        links = (8 if prepared else 3) if name == '@root' else 8 if name == 'pt-coverage' else 2
        if set(value) != expected or m[2:6] != [*owner,stat.S_IFDIR|mode,links]:
            raise ValueError('namespace finite delta refused')
    return True


def durable_reservation(directory_fd, name, data):
    """New fixed private reservation only; partial writes remain non-replayable."""
    if (type(directory_fd) is not int or directory_fd < 0 or type(name) is not str
        or re.fullmatch('[1-9][0-9]*\\.term-reserved\\.private\\.json', name) is None
        or type(data) is not bytes or not 0 < len(data) <= 4096):
        raise ValueError('TERM reservation contract refused')
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o600, dir_fd=directory_fd)
    try:
        os.fchmod(fd, 0o600)
        offset = 0
        while offset < len(data):
            written = os.write(fd, data[offset:])
            if written <= 0:
                raise OSError('TERM reservation write incomplete')
            offset += written
        os.fsync(fd)
    finally:
        os.close(fd)
    os.fsync(directory_fd)


def terminate_once(pid, ticks, verify, reserve, open_pidfd, send, wait, close):
    """Reservation callback must durably O_EXCL/fsync before this single send.

    Errors never imply normal completion and never trigger another signal.
    Caller must retain its exclusion/Refs/FD scope on ANY uncertain result.
    """
    before = verify(pid, ticks)
    fd = open_pidfd(pid)
    primary = None
    try:
        if verify(pid, ticks) != before:
            raise ValueError('owned generation changed before reservation')
        reserve(pid, before)
        if verify(pid, ticks) != before:
            raise ValueError('owned generation changed after reservation')
        send(fd)
        if not wait(fd):
            raise ValueError('owned TERM not terminal')
    except BaseException as failure:
        primary = failure
        raise
    finally:
        try:
            close(fd)
        except BaseException:
            if primary is None:
                raise
            primary.add_note('pidfd close also unknown; isolation must remain')
