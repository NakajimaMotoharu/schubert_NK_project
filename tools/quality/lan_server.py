"""Pinned mini-only SSH for the user-authorized isolated PG/PT server.

Credentials remain local and are sent only after host-key verification. No
password is placed in arguments, environment, diagnostic output or Git.
"""
import argparse
import base64
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import subprocess
import tempfile

import pexpect

HOST = "192.168.1.131"
PIN = "SHA256:D2SRHH06v5k3NLTxDhtS6CWmTkigjotrA7l6XaXWcfA"
INFO = Path("/home/mini/codex/project1/server.info")


def credentials():
    # server.info may hold other machines. Select the already-authorized host
    # section first; never let a later machine overwrite its login identity.
    sections = []
    section = None
    for line in INFO.read_text().splitlines():
        item = re.match(r"^\s*(addr|user|pass)\s*(?:[:=]\s*|\s+)(.*?)\s*$", line)
        if not item:
            continue
        label, value = item.groups()
        if label == "addr":
            section = (value, [])
            sections.append(section)
        elif section is not None:
            section[1].append((label, value))
    matching = [records for address, records in sections if address == HOST]
    if len(matching) != 1:
        raise RuntimeError("Unique authorized host credential section required")
    username = None
    password = None
    mini_records = 0
    for label, value in matching[0]:
        if label == "user":
            if not value:
                raise RuntimeError("Authorized host username required")
            username = value
            if username == "mini":
                mini_records += 1
        elif username == "mini" and label == "pass":
            if password is not None:
                raise RuntimeError("Ambiguous authorized mini credential refused")
            password = value
        elif label == "pass" and username is None:
            raise RuntimeError("Authorized host credential order refused")
    if mini_records != 1 or not password:
        raise RuntimeError("Local mini credential/address contract mismatch")
    return password


def pinned_key():
    scan = subprocess.run(["ssh-keyscan", "-T", "5", "-t", "ed25519", HOST],
                          capture_output=True, check=True, text=True)
    keys = []
    for line in scan.stdout.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[1] == "ssh-ed25519":
            fingerprint = "SHA256:" + base64.b64encode(
                hashlib.sha256(base64.b64decode(fields[2], validate=True)).digest()
            ).decode().rstrip("=")
            if fields[0] != HOST or fingerprint != PIN:
                raise RuntimeError("SSH host identity mismatch; authentication refused")
            keys.append(line)
    if len(set(keys)) != 1:
        raise RuntimeError("SSH host identity unavailable or ambiguous")
    return keys[0]


def ssh_options(known):
    return ["-o", "StrictHostKeyChecking=yes", "-o", f"UserKnownHostsFile={known}",
            "-o", "GlobalKnownHostsFile=/dev/null", "-o", "HostKeyAlgorithms=ssh-ed25519",
            "-o", "PubkeyAuthentication=no", "-o", "PreferredAuthentications=password",
            "-o", "NumberOfPasswordPrompts=1", "-o", "ConnectTimeout=10"]


def authenticated(argv, known, timeout, sudo=False):
    child = pexpect.spawn(argv[0], argv[1:], encoding="utf-8", timeout=timeout, echo=False)
    try:
        child.expect(r"(?i)password:")
        child.sendline(credentials())
        output = ""
        if sudo:
            state = child.expect([r"\[PGPT-SUDO\]", pexpect.EOF])
            output += child.before
            if state == 0:
                child.sendline(credentials())
                child.expect(pexpect.EOF)
                output += child.before
        else:
            child.expect(pexpect.EOF)
            output = child.before
    finally:
        # BUG1098/YKT867: close our exact local child even on timeout/auth error.
        # This is not proof that a remote mutating job completed or was stopped.
        child.close(force=True)
    if child.exitstatus is None:
        raise RuntimeError("SSH ended without an exit status")
    return child.exitstatus, output


def run(command, timeout=60, sudo=False):
    key = pinned_key()  # Before credentials are read or sent.
    with tempfile.TemporaryDirectory(prefix="pgpt-pinned-ssh-") as directory:
        known = Path(directory) / "known_hosts"
        known.write_text(key + "\n")
        os.chmod(known, 0o600)
        if sudo:
            command = "sudo -S -p '[PGPT-SUDO]' -- sh -c " + shlex.quote(command)
        return authenticated(["ssh", "-T", *ssh_options(known), f"mini@{HOST}", command],
                             known, timeout, sudo)


def copy(source, destination, timeout=1800):
    # BUG1097/YKT866: reject lexical escapes before key scan/authentication.
    if (type(destination) is not str or any(ord(c) < 32 for c in destination)
            or not destination.startswith("/home/mini/schubert-nk-pgpt/")
            or re.fullmatch(r"/[A-Za-z0-9_./-]+", destination) is None
            or any(p in {".", ".."} for p in destination.split("/"))
            or str(PurePosixPath(destination)) != destination.rstrip("/")):
        raise ValueError("Transfer destination outside dedicated PGPT region")
    key = pinned_key()
    with tempfile.TemporaryDirectory(prefix="pgpt-pinned-ssh-") as directory:
        known = Path(directory) / "known_hosts"
        known.write_text(key + "\n")
        os.chmod(known, 0o600)
        remote_shell = shlex.join(["ssh", *ssh_options(known)])
        return authenticated(["rsync", "-a", "--partial", "--stats", "--secluded-args", "-e", remote_shell,
                              source, f"mini@{HOST}:{destination}"], known, timeout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--sudo", action="store_true")
    args = parser.parse_args()
    code, output = run(args.command, args.timeout, args.sudo)
    print(output, end="")
    raise SystemExit(code)
