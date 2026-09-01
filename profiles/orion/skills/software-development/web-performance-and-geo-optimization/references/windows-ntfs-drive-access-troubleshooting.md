# Windows NTFS Permissions & Drive Inaccessibility Troubleshooting

## Symptom & Error
- Pop-up dialog: `Location is not available - [Drive]:\ is not accessible. Access is denied.`
- Occurs after OS updates, partition changes, permission misconfigurations, or filesystem security corruption.

## Root Cause
Windows NTFS security descriptor lost ownership or valid Access Control Entries (ACEs) for the local Administrators / Users groups.

## Resolution Workflow

### 1. Elevated Command Prompt (Admin Required)
Standard user command prompt (`C:\Users\<user>>`) will fail with `ERROR: Access is denied.` when executing `takeown`.
- Run CMD as Administrator (`C:\Windows\system32>`).

### 2. Command-Line Fix (Fastest & Automated)
```cmd
:: 1. Take recursive ownership of the entire drive for Administrators
takeown /f D:\ /a /r /d y

:: 2. Grant full control permissions recursively
icacls D:\ /grant Administrators:F /t /c /q
icacls D:\ /grant Everyone:F /t /c /q
```

### 3. Filesystem Error Recovery (If Partition Appears RAW or Corrupted)
```cmd
chkdsk D: /f /r
```
Reboot the system after checking to refresh volume mounts.
