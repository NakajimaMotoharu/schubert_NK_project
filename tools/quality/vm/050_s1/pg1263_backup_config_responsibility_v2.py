"""SS3432/3/6 separates signed release templates from deployed host inputs."""
import hashlib
import re

TEMPLATES={'common.yml':'config/templates/common.yml','api.yml':'config/templates/api.yml','web.yml':'config/templates/web.yml','batch.yml':'config/templates/batch.yml'}
EFFECTIVE={'backup-profile.json':'config/effective/backup-profile.json'}
HOST_ENV={'api.env','web.env','inbox-inspector.env'}
NAMES=set(TEMPLATES)|set(EFFECTIVE)|HOST_ENV

def verify_member(name,archive_bytes,source_bytes,source_identity,archive_identity,expected_gid,signed_hashes):
    if type(name)is not str or name not in NAMES or type(archive_bytes)is not bytes or type(source_bytes)is not bytes or type(signed_hashes)is not dict or type(expected_gid)is not int or expected_gid<1:
        raise ValueError('explicit Backup config responsibility refused')
    mode=0o600 if name in {'api.env','web.env'}else 0o640
    if type(source_identity)is not tuple or type(archive_identity)is not tuple or source_identity!=(0,expected_gid,mode)or archive_identity!=source_identity or archive_bytes!=source_bytes:
        raise ValueError('fixed host Backup config identity/bytes refused')
    if name in EFFECTIVE or name in TEMPLATES:
        path=(EFFECTIVE if name in EFFECTIVE else TEMPLATES)[name]
        digest=signed_hashes.get(path)
        if type(digest)is not str or re.fullmatch('[0-9a-f]{64}',digest)is None:
            raise ValueError('explicit registered release material required')
        if name in EFFECTIVE:
            if hashlib.sha256(archive_bytes).hexdigest()!=digest:raise ValueError('signed effective Backup profile bytes refused')
            return 'SIGNED_EFFECTIVE_PROFILE_AND_FIXED_HOST_BYTES'
        return 'SIGNED_TEMPLATE_REGISTERED_DEPLOYED_HOST_BYTES_NOT_TEMPLATE_BYTE_AUTHORITY'
    return 'EXTERNAL_HOST_ENV_FIXED_INODE_BYTES_NOT_SIGNED_PAYLOAD'
