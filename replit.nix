{pkgs}: {
  deps = [
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
