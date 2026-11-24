# Relatório da Parte 1: Pré-processamento e organização das imagens

**Aluno:** Richard Schmitz | **RM:** 567951 | **Turma:** 2TIAOR-2026 | **Fase 4:** Pulso, Assistente Cardiológico Virtual com Visão Computacional

Notebook de referência: [`notebooks/01_preprocessamento.ipynb`](../notebooks/01_preprocessamento.ipynb). Todos os números abaixo vêm da execução desse notebook ([`resultados/pipeline_resumo.json`](../resultados/pipeline_resumo.json) e [`resultados/splits.csv`](../resultados/splits.csv)).

## 1. Objetivo

Preparar radiografias de tórax para treinar redes neurais convolucionais que detectam **cardiomegalia** (aumento da silhueta cardíaca): selecionar o dataset, pré-processar as imagens (redimensionamento, normalização e conversão de formato), criar os conjuntos de treino, validação e teste e documentar as decisões.

## 2. Dataset

NIH Chest X-rays, versão amostra, obtida do Kaggle (`nih-chest-xrays/sample`), com 5.606 radiografias frontais e um CSV de rótulos, sexo, idade e projeção. O provedor é o NIH Clinical Center. Os rótulos foram extraídos dos laudos por processamento de linguagem natural (Wang et al., CVPR 2017) e não têm validação clínica independente neste projeto. Segundo a documentação do Google Cloud para o dataset do NIH, não há restrições de uso, mas é preciso citar o artigo, linkar o site de download do NIH e reconhecer o NIH Clinical Center. As imagens originais têm 1024 x 1024 pixels (amostra de 300 imagens conferida).

## 3. Etapas do pipeline e justificativas

| Etapa | Escolha | Justificativa |
|---|---|---|
| Rótulo | Cardiomegalia (1) se o laudo contém `Cardiomegaly`. Sem achados (0) se o laudo é `No Finding` | Mantém o foco cardiovascular e dá um problema binário |
| Exclusão | Imagens com outras doenças e sem cardiomegalia (2.421) | Evita um rótulo 0 ambíguo. Limitação: o modelo não é testado contra outras doenças |
| Metadados | Idade inválida (negativa ou acima de 100 anos) vira valor ausente | Não se troca dado inválido por valor plausível |
| Conversão de formato | Escala de cinza, 1 canal | Radiografia é monocromática |
| Redimensionamento | 224 x 224, interpolação LANCZOS | Entrada padrão de VGG16 e ResNet, usadas no Transfer Learning |
| Normalização | 0 a 255 para 0 a 1, aplicada dentro do modelo (Notebook 2) | Os arquivos ficam em `uint8`, menores. A normalização de cada modelo fica no próprio modelo |
| Formato salvo | Arrays `uint8` em `.npz` | Carregamento rápido, sem decodificar PNG a cada época |
| Divisão | **Por paciente**, estratificada pelo rótulo, cerca de 70% / 15% / 15% (`StratifiedGroupKFold`, semente 42) | O mesmo paciente tem várias imagens (média de 1,15, máximo de 6). Dividir por imagem colocaria o mesmo paciente em treino e teste e inflaria as métricas |
| Aumento de dados | Definido no Notebook 2, sem espelhamento horizontal | Espelhar troca o lado do coração |

## 4. Resultado

3.185 imagens ficaram no experimento (3.044 sem achados e 141 com cardiomegalia, prevalência de 4,43%), de 2.762 pacientes.

| Partição | Imagens | Pacientes | Positivos | Prevalência | Sexo F | Sexo M |
|---|---|---|---|---|---|---|
| Treino | 2.277 | 1.975 | 100 | 4,39% | 990 | 1.287 |
| Validação | 462 | 392 | 22 | 4,76% | 232 | 230 |
| Teste | 446 | 395 | 19 | 4,26% | 194 | 252 |

A prevalência é parecida nas três partições, o que mostra que a estratificação funcionou. O teste tem só 19 positivos, e o notebook emite um aviso por isso: métricas e comparações entre grupos devem ser lidas como hipóteses.

## 5. Verificações de qualidade

- Cada registro do CSV tem a imagem correspondente (registros sem imagem: 0).
- O notebook confere por `assert` que nenhum paciente aparece em mais de uma partição.
- A conferência visual de 4 imagens de cada classe, antes e depois do pré-processamento, não mostrou corte, inversão ou área em branco (`assets/nb1_exemplos_preprocessamento.png`).
- Idades: 3.184 de 3.185 registros têm idade válida e 1 foi marcado como inválido. Na primeira execução, a coluna de idade (texto, como `058Y`) foi convertida em ausente sem aviso. O parsing foi corrigido e o notebook agora para com erro se nenhuma idade for lida.

## 6. Limitações

- Rótulos de laudos, sem validação clínica independente.
- Poucos positivos (141 no total), especialmente no teste (19).
- Imagens com outras doenças foram excluídas.
- A redução de 1024 x 1024 para 224 x 224 perde resolução e pode apagar detalhes finos.
- As imagens e os arrays não estão no repositório (volume e atribuição). Eles são gerados pelo Notebook 1 no Google Drive.

## 7. Reprodução

Executar o Notebook 1 no Google Colab com as credenciais do Kaggle nos Secrets (`KAGGLE_USERNAME` e `KAGGLE_KEY`). Nunca versionar o `kaggle.json`.

*Projeto acadêmico. Nada neste relatório produz diagnóstico nem deve apoiar decisão clínica.*
