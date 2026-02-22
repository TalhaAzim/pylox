# Python dependencies for pylox
{ pkgs, ... }: {
  packages = with pkgs; [
    (python313.withPackages (pypkgs: with pypkgs; [
      python-lsp-server
    ]))
  ];
}
