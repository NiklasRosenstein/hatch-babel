# hatch-babel

A hatch build-hook to compile Babel `*.po` files to `*.mo` files at build time.

## Usage

```toml
[build-system]
requires = ["hatchling", "hatch-babel"]
build-backend = "hatchling.build"

[tool.hatch.build.hooks.babel]
locale_dir = "pytr/locale"
include_po = false
```

## Configuration

### `locale_dir: str`

Relative path to the directory that contains the `*.po` files. Example layout:

```
mypkg/
    locale/
        de/LC_MESSAGES/messages.po
        en/LC_MESSAGES/messages.po
        fr/LC_MESSAGES/messages.po
        es/LC_MESSAGES/messages.po
pyproject.toml
```

Your `locale_dir` would be `mypkg/locale`.

### `include_po: bool`

Whether to include the `*.po` files in the build artifact. Default is `false`.
