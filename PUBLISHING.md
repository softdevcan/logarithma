# 🚀 Publishing Guide

Quick reference for publishing new versions to GitHub and PyPI.

## Pre-Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Examples working

## Version Update

1. Update version in `pyproject.toml` and `src/logarithma/__init__.py`
2. Update `CHANGELOG.md` with new features/fixes
3. Create release notes (optional): `RELEASE_NOTES_vX.X.X.md`

## Publishing Commands

### 1. GitHub Release

```bash
# Stage and commit all changes
git add .
git commit -m "Release vX.X.X: Brief description"

# Push to GitHub
git push origin main

# Create and push tag
git tag -a vX.X.X -m "Version X.X.X: Description"
git push origin vX.X.X
```

### 2. PyPI Release

```bash
# Install/upgrade build tools (first time only)
pip install --upgrade build twine

# Clean old builds
rmdir /s /q dist build src\logarithma.egg-info 2>nul

# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

**Note**: You'll need PyPI API token. Create one at https://pypi.org/manage/account/token/

### 3. GitHub Release Page (Optional)

1. Go to https://github.com/softdevcan/logarithma/releases
2. Click "Create a new release"
3. Select tag `vX.X.X`
4. Add title and description
5. Publish

## Verification

```bash
# Test installation
pip install --upgrade logarithma

# Verify version
python -c "import logarithma; print(logarithma.__version__)"
```

## Quick Version Bump

```bash
# Example: v0.2.0 → v0.3.0
# 1. Update versions in files
# 2. Run these commands:
git add . && git commit -m "Release v0.3.0" && git push
git tag -a v0.3.0 -m "Version 0.3.0" && git push origin v0.3.0
rmdir /s /q dist build src\logarithma.egg-info 2>nul
python -m build && python -m twine upload dist/*
```
