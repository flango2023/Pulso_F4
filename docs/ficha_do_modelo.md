# Ficha do modelo - Pulso Fase 4 - classificador de cardiomegalia em radiografia de torax (prototipo academico)

## Contrato de uso
- Entrada: radiografia de torax frontal, escala de cinza, 224 x 224, uint8 (0 a 255), 1 canal, pre-processada como no Notebook 1 (LANCZOS)
- Saida: pontuacao de 0 a 1, nao calibrada, que nao representa probabilidade de doenca
- Decisao: imagem sinalizada para revisao se pontuacao >= 0.35
- Aviso: Projeto academico. Nao e diagnostico e nao deve apoiar decisao clinica.

## Desempenho no teste (446 imagens, 19 positivos)
- recall: 0.895 (IC95% 0.687 a 1.000)
- precisao: 0.108 (IC95% 0.045 a 0.183)
- f1: 0.193 (IC95% 0.085 a 0.306)
- auc_roc: 0.845 (IC95% 0.748 a 0.908)
- auc_pr: 0.157 (IC95% 0.059 a 0.345)

## Diferencas entre mulheres e homens no teste (F menos M)
- taxa_de_sinalizacao: F 0.325 | M 0.373 | dif -0.048 (IC95% -0.142 a 0.045). IC inclui 0: diferenca nao demonstrada
- recall: F 0.889 | M 0.900 | dif -0.011 (IC95% -0.301 a 0.573). IC inclui 0: diferenca nao demonstrada
- falsos_positivos: F 0.297 | M 0.351 | dif -0.054 (IC95% -0.145 a 0.032). IC inclui 0: diferenca nao demonstrada
- precisao: F 0.127 | M 0.096 | dif 0.031 (IC95% -0.094 a 0.153). IC inclui 0: diferenca nao demonstrada
- auc_roc: F 0.843 | M 0.855 | dif -0.013 (IC95% -0.135 a 0.243). IC inclui 0: diferenca nao demonstrada

## Limitacoes
- Teste com apenas 19 casos positivos (9 F e 10 M): todas as metricas tem intervalos largos e devem ser lidas como hipoteses.
- Precisao de 11% no teste: a maior parte das imagens sinalizadas nao tem cardiomegalia no laudo.
- Acuracia de 68% no teste, abaixo da referencia que responde sempre 'sem achados' (96%). A acuracia nao serve como metrica aqui.
- Imagens com outras doencas foram excluidas: o modelo nao foi testado em distinguir cardiomegalia de outros achados.
- O dataset registra apenas sexo binario (M ou F). Outras identidades nao puderam ser avaliadas.
- Resultados variam entre execucoes e entre CPU e GPU: no Notebook 3, 2 de 446 decisoes mudaram entre as duas.
- Limiar escolhido na validacao, que tem poucos positivos.
- Treinado e testado em uma unica fonte de dados (NIH). Sem validacao externa.

## Uso pretendido
- demonstracao academica e estudo de visao computacional em saude

## Fora do escopo
- diagnostico
- triagem de pacientes reais
- apoio a decisao clinica
- equipamentos ou populacoes diferentes do dataset NIH
