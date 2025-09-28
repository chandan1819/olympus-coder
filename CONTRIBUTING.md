# Contributing to Olympus-Coder

Thank you for your interest in contributing to Olympus-Coder! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use the issue templates** when available
3. **Provide detailed information**:
   - Operating system and version
   - Python version
   - Ollama version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs

### Suggesting Features

1. **Check the roadmap** and existing feature requests
2. **Open a discussion** before implementing large features
3. **Provide clear use cases** and benefits
4. **Consider backwards compatibility**

### Code Contributions

#### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/olympus-coder.git
   cd olympus-coder
   ```

2. **Set up development environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

#### Code Standards

- **Python**: Follow PEP 8, use type hints, include docstrings
- **JavaScript**: Use ESLint configuration, JSDoc comments
- **Shell scripts**: Use shellcheck, include error handling
- **Documentation**: Update relevant docs with code changes

#### Testing Requirements

- **Unit tests**: All new functions must have unit tests
- **Integration tests**: Test integration points with Ollama
- **Validation tests**: Ensure model responses meet quality standards
- **Performance tests**: Verify performance targets are met

```bash
# Run all tests
python3 scripts/validate.py --comprehensive
cd validation && python3 test_all_validation.py
cd tests/integration && python3 run_integration_tests.py
```

#### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add or update tests
   - Update documentation

3. **Test thoroughly**
   ```bash
   # Run validation suite
   python3 scripts/validate.py --quick
   
   # Run specific tests
   cd validation && python3 test_all_validation.py
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new validation framework for tool responses"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Fill out PR template** with:
   - Description of changes
   - Testing performed
   - Breaking changes (if any)
   - Related issues

## 📋 Development Guidelines

### Code Organization

```
olympus-coder/
├── config/          # Configuration files
├── integration/     # Python integration layer
├── modelfile/       # Ollama model definitions
├── prompts/         # System prompts and templates
├── scripts/         # Build and deployment scripts
├── tests/           # Test suites
├── validation/      # Validation framework
└── docs/           # Documentation
```

### Commit Message Format

Use conventional commits:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions or modifications
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

### Testing Strategy

#### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Achieve >90% code coverage

#### Integration Tests
- Test Ollama API integration
- Validate model responses
- Test configuration loading

#### End-to-End Tests
- Test complete workflows
- Validate real-world scenarios
- Performance benchmarking

#### Validation Tests
- Code quality assessment
- Response format validation
- Context consistency checks

### Documentation Requirements

- **Code documentation**: Docstrings for all public functions
- **API documentation**: Update integration examples
- **User documentation**: Update README and guides
- **Developer documentation**: Update this file and technical docs

## 🏗️ Architecture Guidelines

### Model Development

When modifying the model:

1. **Test with base models** (CodeLlama, Llama3)
2. **Validate prompt changes** with test scenarios
3. **Measure performance impact** on key metrics
4. **Update configuration** files appropriately

### Integration Layer

When modifying the integration layer:

1. **Maintain backwards compatibility** when possible
2. **Add comprehensive error handling**
3. **Include logging and monitoring**
4. **Update type hints and documentation**

### Validation Framework

When adding validation:

1. **Follow existing patterns** in validation/
2. **Add both positive and negative test cases**
3. **Include performance benchmarks**
4. **Update test runners** appropriately

## 🎯 Performance Standards

### Response Quality
- Structured response accuracy: >95%
- Code syntax correctness: >98%
- Context consistency: >90%

### Performance Targets
- Response time: <5 seconds (typical)
- Memory usage: <2GB (during inference)
- Autonomous completion rate: >75%

### Testing Coverage
- Unit test coverage: >90%
- Integration test coverage: >80%
- End-to-end scenario coverage: >70%

## 🚀 Release Process

### Version Numbering

We use semantic versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Checklist

1. **Update version numbers** in relevant files
2. **Run comprehensive test suite**
3. **Update CHANGELOG.md**
4. **Create release notes**
5. **Tag the release**
6. **Update documentation**

## 🤔 Questions?

- **General questions**: Open a [Discussion](https://github.com/yourusername/olympus-coder/discussions)
- **Bug reports**: Create an [Issue](https://github.com/yourusername/olympus-coder/issues)
- **Feature requests**: Start with a [Discussion](https://github.com/yourusername/olympus-coder/discussions)

## 📄 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

Thank you for contributing to Olympus-Coder! 🙏