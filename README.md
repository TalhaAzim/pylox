Get started by customizing your environment (defined in the .idx/dev.nix file) with the tools and IDE extensions you'll need for your project!

Learn more at https://developers.google.com/idx/guides/customize-idx-env

## Nix Flake Development Environment

This repository includes a `flake.nix` file that defines a reproducible development environment. If you have Nix installed (see https://nixos.org/download.html), you can activate this environment by running the following command in the root of the repository:

```bash
nix develop
```

This will provide a shell with Python 3.13 and other development tools specified in `flake.nix`.