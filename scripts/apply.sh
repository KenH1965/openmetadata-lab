#!/usr/bin/env bash
set -euo pipefail

echo "[validate] yamllint ..."
yamllint -c .yamllint .

if compgen -G "config/k8s/*.{yml,yaml}" > /dev/null; then
  echo "[validate] kubeconform ..."
  kubeconform -ignore-missing-schemas -summary -verbose config/k8s
fi

if compgen -G "config/k8s/*.{yml,yaml}" > /dev/null; then
  echo "[apply] kubectl apply -f config/k8s/"
  kubectl apply -f config/k8s/
else
  echo "No K8s manifests found in config/k8s/. Skipping kubectl apply."
fi

echo "Done."
