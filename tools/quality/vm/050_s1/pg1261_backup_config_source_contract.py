"""SS3418-name archive input vs signed payload vs external host env, explicit only."""
import hashlib

SIGNED={'common.yml':'config/templates/common.yml','api.yml':'config/templates/api.yml','web.yml':'config/templates/web.yml','batch.yml':'config/templates/batch.yml','backup-profile.json':'config/effective/backup-profile.json'}
HOST={'api.env','web.env','inbox-inspector.env'}
NAMES=set(SIGNED)|HOST

def verify_member(name,archive_bytes,source_bytes,source_identity,archive_identity,expected_gid,signed_hashes):
    if type(name)is not str or name not in NAMES or type(archive_bytes)is not bytes or type(source_bytes)is not bytes or type(signed_hashes)is not dict or type(expected_gid)is not int or expected_gid<1:
        raise ValueError('explicit Backup config source contract refused')
    mode=0o600 if name in {'api.env','web.env'}else 0o640
    if type(source_identity)is not tuple or type(archive_identity)is not tuple or source_identity!=(0,expected_gid,mode)or archive_identity!=source_identity or archive_bytes!=source_bytes:
        raise ValueError('Backup config source identity/bytes refused')
    if name in SIGNED:
        path=SIGNED[name]
        if path not in signed_hashes or hashlib.sha256(archive_bytes).hexdigest()!=signed_hashes[path]:
            raise ValueError('explicit signed Backup config source refused')
        return 'SIGNED_PAYLOAD_AND_FIXED_HOST_SOURCE'
    return 'EXTERNAL_HOST_ENV_FIXED_INODE_BYTES_NOT_SIGNED_PAYLOAD'
