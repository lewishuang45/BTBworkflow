# Public release checklist

Before pushing `BTBworkflow` to GitHub, confirm:

- `.env` is not present in the repository history.
- API keys and internal endpoints are stored only in local environment files.
- Generated outputs and runtime state files are excluded by `.gitignore`.
- Example data is safe to publish.
- Internal notes, logs, and one-off debug artifacts are removed.

If the repository was previously committed with real secrets, rotate those secrets before publishing.

