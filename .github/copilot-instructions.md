This is a Python based repository for a python CLI tool.  It is primarily used for downloading markets and financial data through vararious APIs, and performing data preprocessing and transformations for input into downstream processes.  Please follow these guidelines when contributing:

## Code Standards

### Concept of the Application
- the CLI tool, `duk`, will have many subprograms.  The general command line signature is `duk <subprogram> [optional arguments]`
- The subprogram will act like a stand-alone application within the duk interface.  Think of it as an independent module from other subprograms.
- For consistency across duk applications the optional arguments should be defined as consistenly as possible. 

### Required Before Each Commit
- Follow best practices for python coding.
- Develop a unit test for each new feature added to the code base.  Use the pytest framework to create unit tests.
- Unit tests should all pass.
- Usage documentation should be written to explain each feature, and documentation should include example use cases.
- Include logging for all new functionality.

### Repository Structure
- `src/`: Source code location.
- `test/`: Unit test location.
- `doc/`: Documentation location.
- `etc/`: Configuration files location.
- `var/`: Default location for application output, including log files.

### Development Flow
- Test: `make test`
- Build: `make build` to set up project in conda environment.
- Install: `make install` to install project as a standalone application independent of conda.
- Linting: `make fmt` to apply linting checks.
- Doc: `make doc` to build man files.
- Dist: `make dist` to create distribution files for uploading to pypi.
- Clean: `make clean` to remove installed files and distritbution builds.

### Key Guidelines
1. Follow Python best practices and idiomatic patterns
2. Maintain existing code structure and organization
3. Use dependency injection patterns where appropriate
4. Write unit tests for new functionality.  Use table-driven unit tests when possible.
5. Document features and provide usage examples.  Suggest changes to the `doc/` folder when appropriate.
6. Follow project versioning guidance as appropriate.
