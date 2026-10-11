#!/usr/bin/env python3
"""
backup_fleet_dual_layer.py - Automated Dual-Layer Backup Engine for Hermes Fleet.

Generates:
1. Declarative complete snapshot: <timestamp>-fleet-complete
2. Disaster Recovery Secrets & Runtime State: secrets-live-<timestamp> (chmod 700/600)

The fleet root is resolved independently of the caller's session environment:
agent sessions export HERMES_HOME=<profile dir>, which must never be mistaken
for the fleet root. A post-copy verification pass aborts with exit 1 if any
expected artifact is missing, so a snapshot can never silently claim success.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

BASE_OFFLOAD = '/mnt/hermes-storage-offload/hermes-fleet-backups'
REPO_DIR = '/root/projects/hermes-fleet-profiles'

PROFILES = [
    'atlas', 'aurora', 'forge', 'frame', 'groupbot', 'lens',
    'nexus', 'orion', 'prism', 'quant', 'radar', 'sentinel', 'testing'
]

ROOT_FILES = [
    ('.env', 'root.env'),
    ('auth.json', 'root.auth.json'),
    ('google_token.json', 'root.google_token.json'),
    ('gsc_service_account.json', 'root.gsc_service_account.json'),
    ('config.yaml', 'root.config.yaml.raw'),
    ('SOUL.md', 'root.SOUL.md'),
    ('USER.md', 'root.USER.md'),
    ('profile.yaml', 'root.profile.yaml'),
    ('channel_directory.json', 'root.channel_directory.json'),
    ('kanban.db', 'root.kanban.db'),
    ('projects.db', 'root.projects.db'),
    ('verification_evidence.db', 'root.verification_evidence.db'),
    ('monetag_tokens.json', 'root.monetag_tokens.json'),
    ('monetag_active_oauth.json', 'root.monetag_active_oauth.json'),
]

ROOT_DIRS = [
    ('memories', 'root_memories'),
    ('cron', 'root_cron'),
    ('plans', 'plans'),
    ('vault', 'vault'),
    ('bot_relay', 'bot_relay'),
]


def resolve_hermes_root():
    """Resolve the fleet root even when HERMES_HOME points at a profile dir.

    Candidates are tried in order and the first one that actually contains a
    profiles/ directory wins; HERMES_ROOT is honored when explicitly set.
    """
    candidates = []
    for var in ('HERMES_ROOT', 'HERMES_HOME'):
        value = os.environ.get(var)
        if value:
            candidates.append(value)
    candidates.append(os.path.join(os.environ.get('HOME', '/root'), '.hermes'))
    candidates.append('/root/.hermes')

    seen = set()
    for candidate in candidates:
        candidate = os.path.abspath(os.path.expanduser(candidate))
        if candidate in seen:
            continue
        seen.add(candidate)
        if os.path.isdir(os.path.join(candidate, 'profiles')):
            return candidate
    raise SystemExit(
        'FATAL: cannot resolve the fleet HERMES root; no candidate contains a profiles/ directory'
    )


def copy_root_layer(hermes_root, secrets_live_dir):
    for src_name, dst_name in ROOT_FILES:
        src_path = os.path.join(hermes_root, src_name)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, os.path.join(secrets_live_dir, dst_name))

    for src_name, dst_name in ROOT_DIRS:
        src_path = os.path.join(hermes_root, src_name)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, os.path.join(secrets_live_dir, dst_name), dirs_exist_ok=True)

    wa_root_src = os.path.join(hermes_root, 'platforms', 'whatsapp', 'session')
    if os.path.isdir(wa_root_src):
        shutil.copytree(wa_root_src, os.path.join(secrets_live_dir, 'root_whatsapp_session'), dirs_exist_ok=True)


def copy_profile_layer(hermes_root, secrets_live_dir):
    for p in PROFILES:
        p_src = os.path.join(hermes_root, 'profiles', p)
        p_dst = os.path.join(secrets_live_dir, p)
        os.makedirs(p_dst, mode=0o700, exist_ok=True)

        for f in ['.env', 'auth.json', 'config.yaml']:
            f_src = os.path.join(p_src, f)
            if os.path.isfile(f_src):
                dest_name = 'config.yaml.raw' if f == 'config.yaml' else f
                shutil.copy2(f_src, os.path.join(p_dst, dest_name))

        for d in ['cron', 'memories']:
            d_src = os.path.join(p_src, d)
            if os.path.isdir(d_src):
                shutil.copytree(d_src, os.path.join(p_dst, d), dirs_exist_ok=True)

        p_whatsapp = os.path.join(p_src, 'whatsapp')
        if os.path.isdir(p_whatsapp):
            shutil.copytree(p_whatsapp, os.path.join(p_dst, 'whatsapp'), dirs_exist_ok=True)

        p_platforms_wa = os.path.join(p_src, 'platforms', 'whatsapp')
        if os.path.isdir(p_platforms_wa):
            shutil.copytree(p_platforms_wa, os.path.join(p_dst, 'platforms_whatsapp'), dirs_exist_ok=True)

        p_vault = os.path.join(p_src, 'vault')
        if os.path.isdir(p_vault):
            shutil.copytree(p_vault, os.path.join(p_dst, 'vault'), dirs_exist_ok=True)


def enforce_permissions(target_dir):
    for root, dirs, files in os.walk(target_dir):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o700)
        for f in files:
            os.chmod(os.path.join(root, f), 0o600)
    os.chmod(target_dir, 0o700)


def _has_entries(path):
    return os.path.isdir(path) and len(os.listdir(path)) > 0


def verify_backup(hermes_root, fleet_complete_dir, secrets_live_dir):
    """Fail-closed verification: any missing expected artifact aborts the run."""
    problems = []

    # Declarative snapshot
    if not os.path.isdir(os.path.join(fleet_complete_dir, 'profiles')):
        problems.append('fleet-complete: missing profiles/ directory')
    for p in PROFILES:
        if not os.path.isdir(os.path.join(fleet_complete_dir, 'profiles', p)):
            problems.append(f'fleet-complete: missing profiles/{p}')
    if os.path.isdir(os.path.join(hermes_root, 'fleet_v2_system')) and not _has_entries(
            os.path.join(fleet_complete_dir, 'fleet_v2_system')):
        problems.append('fleet-complete: missing or empty fleet_v2_system/')
    if os.path.isdir(os.path.join(hermes_root, 'plugins')) and not _has_entries(
            os.path.join(fleet_complete_dir, 'plugins')):
        problems.append('fleet-complete: missing or empty plugins/')

    # Root secrets layer
    for src_name, dst_name in ROOT_FILES:
        if os.path.isfile(os.path.join(hermes_root, src_name)) and not os.path.isfile(
                os.path.join(secrets_live_dir, dst_name)):
            problems.append(f'secrets: missing {dst_name}')
    for src_name, dst_name in ROOT_DIRS:
        if os.path.isdir(os.path.join(hermes_root, src_name)) and not os.path.isdir(
                os.path.join(secrets_live_dir, dst_name)):
            problems.append(f'secrets: missing {dst_name}/')
    if os.path.isdir(os.path.join(hermes_root, 'platforms', 'whatsapp', 'session')) and not os.path.isdir(
            os.path.join(secrets_live_dir, 'root_whatsapp_session')):
        problems.append('secrets: missing root_whatsapp_session/')

    # Per-profile layer
    for p in PROFILES:
        p_src = os.path.join(hermes_root, 'profiles', p)
        p_dst = os.path.join(secrets_live_dir, p)
        if not os.path.isdir(p_src):
            problems.append(f'secrets: live profile missing: {p_src}')
            continue
        for src_name, dst_name in (('.env', '.env'), ('auth.json', 'auth.json'), ('config.yaml', 'config.yaml.raw')):
            if os.path.isfile(os.path.join(p_src, src_name)) and not os.path.isfile(
                    os.path.join(p_dst, dst_name)):
                problems.append(f'secrets: {p}/{dst_name} missing')
        for d in ('cron', 'memories'):
            if os.path.isdir(os.path.join(p_src, d)) and not os.path.isdir(os.path.join(p_dst, d)):
                problems.append(f'secrets: {p}/{d}/ missing')
        for src_rel, dst_name in (('whatsapp', 'whatsapp'),
                                  (os.path.join('platforms', 'whatsapp'), 'platforms_whatsapp'),
                                  ('vault', 'vault')):
            if os.path.isdir(os.path.join(p_src, src_rel)) and not os.path.isdir(
                    os.path.join(p_dst, dst_name)):
                problems.append(f'secrets: {p}/{dst_name}/ missing')

    if problems:
        print('BACKUP VERIFICATION FAILED:')
        for problem in problems:
            print(f'  - {problem}')
        raise SystemExit(1)
    print('-> Verification passed: all expected root, profile, and platform artifacts present.')


def run_backup():
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    hermes_root = resolve_hermes_root()
    print(f"Starting Comprehensive Hermes Fleet Dual-Layer Backup: {timestamp}")
    print(f"-> Fleet root resolved: {hermes_root}")

    fleet_complete_dir = os.path.join(BASE_OFFLOAD, f"{timestamp}-fleet-complete")
    secrets_live_dir = os.path.join(BASE_OFFLOAD, f"secrets-live-{timestamp}")

    # 1. Declarative complete snapshot
    os.makedirs(fleet_complete_dir, exist_ok=True)
    subprocess.run([
        'cp', '-a',
        os.path.join(REPO_DIR, 'global'),
        os.path.join(REPO_DIR, 'profiles'),
        fleet_complete_dir,
    ], check=True)

    fleet_v2_src = os.path.join(hermes_root, 'fleet_v2_system')
    if os.path.isdir(fleet_v2_src):
        subprocess.run(['rsync', '-a', '--exclude=__pycache__', fleet_v2_src, fleet_complete_dir], check=True)

    plugins_src = os.path.join(hermes_root, 'plugins')
    if os.path.isdir(plugins_src):
        subprocess.run(['rsync', '-a', '--exclude=__pycache__', '--exclude=.git', plugins_src, fleet_complete_dir], check=True)

    print(f"-> Declarative complete snapshot: {fleet_complete_dir}")

    # 2. Disaster Recovery Secrets & Runtime State Layer
    os.makedirs(secrets_live_dir, mode=0o700, exist_ok=True)
    copy_root_layer(hermes_root, secrets_live_dir)
    copy_profile_layer(hermes_root, secrets_live_dir)

    # Enforce strict POSIX permissions, then fail-closed verification
    enforce_permissions(secrets_live_dir)
    verify_backup(hermes_root, fleet_complete_dir, secrets_live_dir)

    print(f"-> Secrets & Runtime State Layer created: {secrets_live_dir}")
    print("-> Enforced strict POSIX 700/600 permissions.")
    print("Comprehensive Dual-Layer Backup Complete!")


if __name__ == '__main__':
    run_backup()
