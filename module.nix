{ config, pkgs, ... }:
{
  deployment.keys.prometheus-packet-spot-market-price-exporter = {
    text = builtins.readFile ./config.json;
  };

  systemd.services.prometheus-packet-spot-market-price-exporter = {
    wantedBy = [ "multi-user.target" ];
    after = [ "network.target" ];
    serviceConfig = {
      Restart = "always";
      RestartSec = "60s";
      PrivateTmp =  true;
    };

    path = [
      (pkgs.python3.withPackages (p: [ p.prometheus_client p.requests ]))
    ];

    script = "exec python3 ${./scrape.py} /run/keys/prometheus-packet-spot-market-price-exporter";
  };
}
