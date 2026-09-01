# GitHub API & Git Sparse Checkout Cheatsheet

## Command Sequence

```bash
# Initialize partial sparse clone
git clone --depth=1 --filter=blob:none --sparse <url> <dest>

# Set specific directories to pull
cd <dest>
git sparse-checkout set <dir1> <dir2>
```

## Verifying Sparse Checkout State

To see what directories are currently checked out:

```bash
git sparse-checkout list
```
