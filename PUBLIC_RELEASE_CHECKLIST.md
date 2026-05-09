# Public Release Checklist

Use this checklist before publishing `BTBworkflow`, sharing a recruiter demo link, or opening the repository to public viewing.

## Must Be True

- `.env` is not tracked.
- `.env.example` contains placeholder values only.
- No real API keys are committed.
- No private endpoints, deployment names, tokens, secrets, or credentials are committed.
- No local absolute paths such as `/Users/...` or `C:\...` are committed in source or docs.
- No email addresses, phone numbers, personal data, or private customer records are present in sample datasets.
- Runtime outputs are ignored unless intentionally placed under `examples/`.
- Generated JSON outputs, logs, uploaded datasets, generated images, and generated HTML reports are not tracked.
- `examples/` contains only small, original, safe-to-publish sample artifacts.

## Secret Scan Commands

Run these before publishing:

```bash
git grep -n -I -E "sk-|api[_-]?key|password|secret|token|endpoint|deployment|openai|azure|anthropic|gemini|/Users|C:\\|gmail|phone"
git log --all -S "api_key"
git log --all -S "sk-"
```

Review matches manually. Placeholder documentation may intentionally mention words such as `endpoint` or `api_key`, but no real values should appear.

## Runtime Artifact Check

```bash
git status --short
git ls-files final_output.json chart_config.json workflow_state.json image_soft_boundary.json mock_presentation.html ppt_mockup.png report_output.html
```

The second command should print nothing unless a file was intentionally moved into `examples/`.

## If A Secret Was Accidentally Committed

1. Revoke or rotate the exposed credential immediately.
2. Remove the secret from the working tree.
3. Rewrite Git history using a trusted tool such as `git filter-repo` or BFG Repo-Cleaner.
4. Force-push only after confirming collaborators understand the history rewrite.
5. Re-run the secret scan commands above.

Do not rely on deleting the latest commit if the secret was pushed or exists elsewhere in history.
