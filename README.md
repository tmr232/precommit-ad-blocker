# Pre-commit Ad-Blocker

Automatically blocks LLM-added co-authored-by trailers from your commit messages.

## Usage

To block commit-message ads in your repo, add the following to your `.pre-commit-config.yaml`:

```yaml
repos:
- repo: https://github.com/tmr232/precommit-ad-blocker
  rev: v1.0.0
  hooks:
    - id: precommit-ad-blocker
```

To block specific co-authors or trailer-keys beyond the defaults, add them to the args:

```yaml
repos:
- repo: https://github.com/tmr232/precommit-ad-blocker
  rev: v1.0.0
  hooks:
    - id: precommit-ad-blocker
      args: [--co-author=*@anthropic.com, --co-author=*@ampcode.com, --trailer=Amp-Thread-ID]
```

To see which lines were blocked, add the `--verbose` arg:

```yaml
repos:
- repo: https://github.com/tmr232/precommit-ad-blocker
  rev: v1.0.0
  hooks:
    - id: precommit-ad-blocker
      args: [--verbose]
```

To disable the defaults co-author and trailer lists, use `--no-defaults`:

```yaml
repos:
- repo: https://github.com/tmr232/precommit-ad-blocker
  rev: v1.0.0
  hooks:
    - id: precommit-ad-blocker
      args: [--no-defaults]
```