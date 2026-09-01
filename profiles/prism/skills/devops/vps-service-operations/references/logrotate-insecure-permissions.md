# Logrotate Insecure Directory Permissions Troubleshooting

## Error Symptoms
When executing manual or scheduled log rotations (`logrotate -f /etc/logrotate.d/rsyslog`), you might encounter errors like:
```text
error: skipping "/var/log/syslog" because parent directory has insecure permissions (It's world writable or writable by group which is not "root") Set "su" directive in config file to tell logrotate which user/group should be used for rotation.
```

## Causes
Logrotate has strict security defaults. If the directory containing the logs (usually `/var/log` or a sub-folder) is group-writable and the group is not `root`, logrotate skips rotating those logs to prevent privilege escalation.

On some systems, `/var/log` might have group `syslog` with write permissions:
`drwxrwxr-x root syslog /var/log`

## Solutions & Mitigations

### Option A: Include the `su` Directive in Logrotate Config (Recommended)
This tells logrotate to drop permissions to the specified user and group before rotating files in that directory.

1. Open `/etc/logrotate.d/rsyslog` or the specific service logrotate configuration.
2. Add `su root syslog` (or the appropriate owner/group combination) inside the block.
   Example:
   ```text
   /var/log/syslog
   /var/log/mail.info
   /var/log/cron
   {
       rotate 4
       weekly
       missingok
       notifempty
       compress
       delaycompress
       sharedscripts
       su root syslog
       postrotate
           /usr/lib/rsyslog/rsyslog-rotate
       endscript
   }
   ```

### Option B: Fix Directory Permissions (If Group Write is Unnecessary)
If the directory does not require group write access:
```bash
chmod 755 /var/log
```
*Note: Verify if system daemons fail to write logs after doing this. If they do, revert using `chmod 775 /var/log` and use Option A.*
