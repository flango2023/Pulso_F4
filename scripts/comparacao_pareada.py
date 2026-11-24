"""Comparacao pareada entre a CNN simples e a ResNet50 (Fase 4, Pulso).

Le as previsoes salvas pelo Notebook 2 e o splits.csv do Notebook 1, e calcula:
- AUC-ROC e AUC-PR de cada modelo na validacao e no teste;
- a diferenca (ResNet50 menos CNN) de AUC-ROC e AUC-PR no teste, com IC de 95% por
  bootstrap pareado que reamostra pacientes (as duas previsoes da mesma imagem entram juntas).

Uso (a partir da raiz do repositorio):
    python scripts/comparacao_pareada.py
Saida: resultados/comparacao_pareada.json
Dependencias: numpy, pandas, scikit-learn.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "resultados"
SEED = 42
N_REP = 2000

splits = pd.read_csv(RES / "splits.csv").set_index("imagem")


def carregar(tipo, modelo):
    return pd.read_csv(RES / ("pred_%s_%s.csv" % (tipo, modelo)))


def auc_par(d):
    return {"auc_roc": float(roc_auc_score(d["y"], d["prob"])), "auc_pr": float(average_precision_score(d["y"], d["prob"]))}


saida = {"semente": SEED, "repeticoes": N_REP, "validacao": {}, "teste": {}}
for tipo, chave in [("val", "validacao"), ("teste", "teste")]:
    for modelo in ["cnn_simples", "resnet50"]:
        d = carregar(tipo, modelo)
        saida[chave][modelo] = {**auc_par(d), "imagens": int(len(d)), "positivos": int(d["y"].sum())}

a, b = carregar("teste", "cnn_simples"), carregar("teste", "resnet50")
assert (a["imagem"] == b["imagem"]).all() and (a["y"] == b["y"]).all(), "Previsoes desalinhadas entre os modelos"
assert (splits.loc[a["imagem"], "particao"] == "teste").all(), "Imagens fora do conjunto de teste"
y = a["y"].values.astype(int)
pac = splits.loc[a["imagem"], "paciente"].values
grupos = [g.index.values for _, g in pd.DataFrame({"pac": pac}).groupby("pac")]
rng = np.random.default_rng(SEED)
dif_roc, dif_pr = [], []
for _ in range(N_REP):
    idx = np.concatenate([grupos[i] for i in rng.integers(0, len(grupos), len(grupos))])
    if y[idx].sum() == 0 or y[idx].sum() == len(idx):
        continue
    dif_roc.append(roc_auc_score(y[idx], b["prob"].values[idx]) - roc_auc_score(y[idx], a["prob"].values[idx]))
    dif_pr.append(average_precision_score(y[idx], b["prob"].values[idx]) - average_precision_score(y[idx], a["prob"].values[idx]))
for nome, v in [("dif_auc_roc_resnet50_menos_cnn", dif_roc), ("dif_auc_pr_resnet50_menos_cnn", dif_pr)]:
    lo, hi = np.percentile(v, [2.5, 97.5])
    saida["teste"][nome] = {"media": float(np.mean(v)), "ic95": [float(lo), float(hi)], "repeticoes_validas": len(v),
                            "leitura": "IC inclui 0: diferenca nao demonstrada" if lo <= 0 <= hi else "IC exclui 0: diferenca observada nesta amostra"}

(RES / "comparacao_pareada.json").write_text(json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(saida, indent=2, ensure_ascii=False))
