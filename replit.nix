{pkgs}: {
  deps = [
    pkgs.gh
    pkgs.gcc
    pkgs.chromium
    pkgs.jq
    pkgs.tree
    pkgs.black
    pkgs.wget
    pkgs.zlib
    pkgs.pkg-config
    pkgs.grpc
    pkgs.c-ares
    pkgs.kubo
    pkgs.postgresql
    pkgs.openssl
  ];
}
