# Workflow
- Be sure to check for the latest code in an entire module before implementing code changes
- Prefer running single tests, and not the whole test suite, for performance
- Comment code where applicable and generate or update README.md files in folders that may require more context or understanding
- Use `pytest` for unit testing
- Consider current folder structure and naming conventions when making code changes or creating new code or modules
- Include Docstrings and code comments whenever additional context may be helpful
- Request permission to add, commit and push to git after implementation milestones or significant code changes
- Address each issue one by one when working through code changes
- Run scripts in python using thr `-m` tag. For example, `python -m scripts.crawler_idx.run_daily_metadata_ingest`.
- Do not yet ask to run tet scripts or execute any code until further notice. In the meantime, I will execute all scripts on a separate platform running Windows 10 using `cmd` terminal in VS Code. 
- Update `README.md` files in each folder or subfolder after implementations have been completed.
- Add brief but useful comments to your code edits where applicable while edting. Also follow up with updating documentation in the README.md file(s) of any associated folders including on the parent or child folder levels.

# Code style
- Maintain the proper separation of concerns when patching code. Do not patch individual files without thinking about the impact on the rest of the codebase.
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')
- Define database joins in SQLAlchemy models and use them in code
- Use `@dataclass` containers whenever possible to pass raw files or strings between modules. Prioritize this over passing raw strings.
- Refrain from adding code to `__init__.py` files to resolve module import errors.
- Always reference the `README.md` file in a particular folder, parent folder(s) and subfolder(s) before finalizing any code edits or implementation.