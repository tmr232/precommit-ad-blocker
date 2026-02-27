# Pre-commit Ad-Blocker

The tools you use are not "co-authors" of your code.

Block LLM-generated "Co-Authored-By" trailers in your commit messages.

## Usage

> [!IMPORTANT]
> Make sure to install `commit-msg` hooks in your repo.
> They are not installed by default.

Install `commit-msg` hooks:

```shell
# Using prek
prek install --hook-type commit-msg

# or pre-commit
pre-commit install --hook-type commit-msg
```

To block commit-message ads in your repo, add the following to your `.pre-commit-config.yaml`:

```yaml
# Install both pre-commit and commit-msg hooks
default_install_hook_types: [pre-commit, commit-msg]

repos:
- repo: https://github.com/tmr232/precommit-ad-blocker
  rev: v1.0.0
  hooks:
    - id: ad-blocker
```

To block specific co-authors or trailer-keys beyond the defaults, add them to the args:

```yaml
default_install_hook_types: [pre-commit, commit-msg]

repos:
- repo: https://github.com/tmr232/precommit-ad-blocker
  rev: v1.0.0
  hooks:
    - id: ad-blocker
      args: [--co-author=*@anthropic.com, --co-author=*@ampcode.com, --trailer=Amp-Thread-ID]
```

To disable the defaults co-author and trailer lists, use `--no-defaults`:

```yaml
default_install_hook_types: [pre-commit, commit-msg]

repos:
- repo: https://github.com/tmr232/precommit-ad-blocker
  rev: v1.0.0
  hooks:
    - id: ad-blocker
      args: [--no-defaults]
```