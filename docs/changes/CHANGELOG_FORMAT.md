# Changelog Format Guide

## Entry Format

Each changelog entry should follow this format:

```markdown
## [VERSION] - YYYY-MM-DD

### Added
- New features added

### Changed
- Changes in existing functionality

### Deprecated
- Features soon to be removed

### Removed
- Features removed

### Fixed
- Bug fixes

### Security
- Security vulnerability fixes
```

## Guidelines

1. Always add entries at the top
2. Use present tense ("Add" not "Added")
3. Include PR/Issue numbers where applicable
4. Group related changes
5. Include migration instructions if needed

## Version Numbers

Follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Incompatible API changes
- MINOR: Add functionality (backwards-compatible)
- PATCH: Bug fixes (backwards-compatible)
