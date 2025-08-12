This is a Python based repository for a python CLI tool.  It is primarily used for downloading markets and financial data through vararious APIs, and performing data preprocessing and transformations for input into downstream processes.  Please follow these guidelines when contributing:

## Code Standards

### Concept of the Application
- the CLI tool, `duk`, will have many subprograms.  The general command line signature is `duk <subprogram> [optional arguments]`
- The subprogram will act like a stand-alone application within the duk interface.  Think of it as an independent module from other subprograms.
- For consistency across duk applications the optional arguments should be defined as consistenly as possible. 

### Required Before Each Commit
- Follow best practices for python coding.
- Develop a unit test for each new feature added to the code base.
- Unit tests should all pass.
- Usage documentation should be written to explain each feature, and documentation should include example use cases.
- Each new feature should include support for logging.

### Repository Structure
- `src/`: Source code location.
- `test/`: Unit test location.
- `doc/`: Documentation location.
- `etc/`: Configuration files location.
- `var/`: Default location for application output, including log files.

### Development Flow
- Test: `make test`
- Install: `make install`

### Project Versioning
- The project version should be reflected in `pyproject.toml` and `src/duk/__init__.py`.
- The project version formatting convention is `<major release>.<minor release>.<bug fix>`.
- All issues associated with an `enhancement` label are considered a minor release.
- All issues associated with a `bug` label are considered a bug fix.
- Only update the major release version when explicitly directed.

### Key Guidelines
1. Follow Python best practices and idiomatic patterns
2. Maintain existing code structure and organization
3. Use dependency injection patterns where appropriate
4. Write unit tests for new functionality.  Use table-driven unit tests when possible.
5. Document features and provide usage examples.  Suggest changes to the `doc/` folder when appropriate.
6. Follow project versioning guidance as appropriate.
