# C dependencies for clox
{ pkgs, ... }: {
  packages = with pkgs; [
    clang
    clang-tools
  ];
}
