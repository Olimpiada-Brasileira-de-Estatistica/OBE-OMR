{
  description = "Ambiente de desenvolvimento Python com OpenCV + GTK";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    allSystems = [
      "x86_64-linux" # 64-bit Intel/AMD Linux
      "aarch64-linux" # 64-bit ARM Linux
      "x86_64-darwin" # 64-bit Intel macOS
      "aarch64-darwin" # 64-bit ARM macOS
    ];

    # system-specific
    forAllSystems = f:
      nixpkgs.lib.genAttrs allSystems (system:
        f {
          pkgs = import nixpkgs {
            inherit system;
            # Overlay do OpenCV Overlay para o NixOS
            overlays = [
              (final: prev: {
                opencv4 = prev.opencv4.override {
                  enableGtk3 = true;
                  enablePython = true;
                };
              })
            ];
          };
        });
  in {
    devShells = forAllSystems ({pkgs}: {
      default = let
        python = pkgs.python313;
      in
        pkgs.mkShell {
          packages = [
            (python.withPackages (ps:
              with ps; [
                numpy
                ipython
                opencv4
              ]))
          ];
          buildInputs = [
            pkgs.pkg-config
            pkgs.stdenv.cc.cc.lib
          ];
          shellHook = ''
            export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH
                        echo "Python pronto com OpenCV $(python -c 'import cv2; print(cv2.__version__)')"
          '';
        };
    });
  };
}
