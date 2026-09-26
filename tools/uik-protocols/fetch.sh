#!/bin/sh
set -e
cd "$(dirname "$0")"
mkdir -p src
for f in uik_protocols.csv.gz uik_single_mandate_full.csv.gz uik_federal_full.csv.gz; do
  curl -sSL -o "src/$f" "https://deg.zhizhin.xyz/$f"
done
