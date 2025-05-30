# Release Checklist

## Pre-Release Checks

### Code Quality
- [ ] All tests passing (`./scripts/test.sh`)
- [ ] Code formatting verified (`black src tests`)
- [ ] Type checking passing (`mypy src`)
- [ ] Linting passing (`flake8 src tests`)
- [ ] Security checks passing (`bandit -r src`)
- [ ] Test coverage at least 80%

### Documentation
- [ ] README.md updated
- [ ] CHANGELOG.md updated
- [ ] Documentation reflects all changes
- [ ] Docstrings complete and up-to-date
- [ ] Example code working
- [ ] API documentation generated

### Docker
- [ ] Production container builds successfully
- [ ] Development container works
- [ ] Container tests passing
- [ ] Security scan clean
- [ ] Multi-platform builds working

### Dependencies
- [ ] Dependencies up to date
- [ ] Requirements files updated
- [ ] Development dependencies current
- [ ] Compatibility verified

## Release Process

1. Version Update
   - [ ] Update version in `src/__init__.py`
   - [ ] Update CHANGELOG.md
   - [ ] Update documentation version references

2. Testing
   - [ ] Run full test suite locally
   - [ ] Run container tests
   - [ ] Verify in clean environment
   - [ ] Check all CI workflows passing

3. Documentation
   - [ ] Generate latest API docs
   - [ ] Update installation instructions
   - [ ] Verify documentation builds
   - [ ] Check all links working

4. Package
   - [ ] Build distribution: `python -m build`
   - [ ] Verify package contents
   - [ ] Check package installs cleanly
   - [ ] Verify entry points working

5. Container
   - [ ] Build final container
   - [ ] Test container functionality
   - [ ] Verify multi-platform builds
   - [ ] Check container size optimized

6. Create Release
   - [ ] Tag release in git
   - [ ] Push to GitHub
   - [ ] Create GitHub release
   - [ ] Add release notes

7. Publish
   - [ ] Upload to PyPI
   - [ ] Push container to registry
   - [ ] Verify installation works
   - [ ] Check documentation published

## Post-Release

1. Verify
   - [ ] PyPI package installable
   - [ ] Container pullable
   - [ ] Documentation accessible
   - [ ] GitHub release visible

2. Announce
   - [ ] Update project status
   - [ ] Notify contributors
   - [ ] Update issue tracker
   - [ ] Close milestone

3. Cleanup
   - [ ] Remove old branches
   - [ ] Archive completed issues
   - [ ] Update project boards
   - [ ] Clean up CI caches

4. Plan Next
   - [ ] Create new milestone
   - [ ] Update roadmap
   - [ ] Schedule next release
   - [ ] Review backlog

