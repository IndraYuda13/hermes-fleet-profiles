#!/usr/bin/env python3
"""
backup_fleet_dual_layer.py - Automated Dual-Layer Backup Engine for Hermes Fleet.

Generates:
1. Declarative complete snapshot: <timestamp>-fleet-complete
2. Disaster Recovery Secrets & Runtime State: secrets-live-<timestamp> (chmod 700/600)
"""

import os
import shutil
import subprocess
from datetime import datetime, timezone

def run_backup():
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    print(f"Starting Comprehensive Hermes Fleet Dual-Layer Backup: {timestamp}")

    base_offload = '/mnt/hermes-storage-offload/hermes-fleet-backups'
    repo_dir = '/root/projects/hermes-fleet-profiles'
    hermes_root = os.environ.get('HERMES_HOME', '/root/.hermes')

    fleet_complete_dir = os.path.join(base_offload, f"{timestamp}-fleet-complete")
    secrets_live_dir = os.path.join(base_offload, f"secrets-live-{timestamp}")

    # 1. Declarative complete snapshot
    os.makedirs(fleet_complete_dir, exist_ok=True)
    subprocess.run(['cp', '-a', os.path.join(repo_dir, 'global'), os.path.join(repo_dir, 'profiles'), fleet_complete_dir], check=True)

    # Sync fleet_v2_system and plugins (excluding .git and caches)
    fleet_v2_src = os.path.join(hermes_root, 'fleet_v2_system')
    if os.path.isdir(fleet_v2_src):
        subprocess.run(['rsync', '-a', '--exclude=__pycache__', fleet_v2_src, fleet_complete_dir], check=True)

    plugins_src = os.path.join(hermes_root, 'plugins')
    if os.path.isdir(plugins_src):
        subprocess.run(['rsync', '-a', '--exclude=__pycache__', '--exclude=.git', plugins_src, fleet_complete_dir], check=True)

    print(f"-> Declarative complete snapshot: {fleet_complete_dir}")

    # 2. Disaster Recovery Secrets & Runtime State Layer
    os.makedirs(secrets_live_dir, mode=0o700, exist_ok=True)

    root_files = [
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

    for src_name, dst_name in root_files:
        src_path = os.path.join(hermes_root, src_name)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, os.path.join(secrets_live_dir, dst_name))

    root_dirs = [
        ('memories', 'root_memories'),
        ('cron', 'root_cron'),
        ('plans', 'plans'),
        ('vault', 'vault'),
        ('bot_relay', 'bot_relay'),
    ]
    for src_name, dst_name in root_dirs:
        src_path = os.path.join(hermes_root, src_name)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, os.path.join(secrets_live_dir, dst_name), dirs_exist_ok=True)

    wa_root_src = os.path.join(hermes_root, 'platforms', 'whatsapp', 'session')
    if os.path.isdir(wa_root_src):
        shutil.copytree(wa_root_src, os.path.join(secrets_live_dir, 'root_whatsapp_session'), dirs_exist_ok=True)

    profiles = [
        'atlas', 'aurora', 'forge', 'frame', 'groupbot', 'lens',
        'nexus', 'orion', 'prism', 'quant', 'radar', 'sentinel', 'testing'
    ]

    for p in profiles:
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

        p_wa_orion = os.path.join(p_src, 'whatsapp')
        if os.path.isdir(p_wa_orion):
            shutil.copytree(p_wa_orion, os.path.join(p_dst, 'whatsapp'), dirs_exist_ok=True)

        p_wa_gb = os.path.join(p_src, 'platforms', 'whatsapp')
        if os.path.isdir(p_wa_gb):
            shutil.copytree(p_wa_gb, os.path.join(p_dst, 'platforms_whatsapp'), dirs_exist_ok=True)

    # Enforce strict POSIX permissions
    for root, dirs, files in os.walk(secrets_live_dir):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o700)
        for f in files:
            os.chmod(os.path.join(root, f), 0o600)
    os.chmod(secrets_live_dir, 0o700)

    print(f"-> Secrets & Runtime State Layer created: {secrets_live_dir}")
    print("-> Enforced strict POSIX 700/600 permissions.")
    print("Comprehensive Dual-Layer Backup Complete!")

if __name__ == '__main__':
    run_backup()
