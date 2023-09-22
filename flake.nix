{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = {self, nixpkgs, flake-utils}:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = import nixpkgs { inherit system; };
          python = pkgs.python3.withPackages (py: [
            py.numpy
            py.matplotlib
          ]);
      in
        {
          devShells.default = pkgs.mkShellNoCC {
            packages = [python];
          };
        });
}
