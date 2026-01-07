{
  description = "Pylox devshell flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }: let 
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    idx = import ./.idx/dev.nix { inherit pkgs };
    in {
     devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
        ] ++ idx.packages;
     }; 
  };
}
