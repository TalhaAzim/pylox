{
  description = "Pylox devshell flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }: let 
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    idx = import ./.idx/dev.nix { inherit pkgs; };
    in {
     devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
        ] ++ idx.packages;
     }; 

     # `nix fmt` formats the clox C sources in the book's style (.clang-format).
     # With no arguments it formats the whole tree; otherwise the given paths.
     formatter.${system} = pkgs.writeShellApplication {
       name = "clox-fmt";
       runtimeInputs = [ pkgs.clang-tools pkgs.findutils ];
       text = ''
         if [ "$#" -eq 0 ]; then set -- .; fi
         find "$@" -name .git -prune -o -type f \( -name '*.c' -o -name '*.h' \) -print0 \
           | xargs -0 --no-run-if-empty clang-format -i
       '';
     };
  };
}
