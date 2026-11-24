# Relatório Ir Além 1 — Ética e Governança em Visão Computacional
**Projeto:** Pulso — Inteligência Cardiológica com Consciência de Dados  
**Fase 4:** Coração em Imagens — Assistente Cardiológico Virtual com Visão Computacional  
**Dataset:** NIH Chest X-rays (versão amostra)  
**Autor:** Richard Schmitz — RM 567951 — Turma 2TIAOR-2026

---

Notebook: [`notebooks/04_fairness_governanca.ipynb`](../notebooks/04_fairness_governanca.ipynb). Tabelas completas: [`resultados/`](../resultados/) e [README](../README.md). Ficha do modelo: [`ficha_do_modelo.md`](ficha_do_modelo.md).

---

## 1. Escopo e método

Analisa as limitações do dataset NIH (amostra) e mede se a CNN do zero e a ResNet50 do Notebook 2 têm desempenho diferente entre grupos. O grupo principal é o **sexo** (eixo do projeto). Também foram analisados faixa etária e projeção da radiografia (AP ou PA). As métricas foram calculadas só no teste (446 imagens, 19 positivos), com o limiar escolhido na validação: taxa de sinalização (paridade demográfica), recall (igualdade de oportunidade), taxa de falsos positivos, precisão (paridade preditiva) e AUC-ROC. Quando a prevalência difere entre grupos, não é possível igualar todas ao mesmo tempo (Chouldechova, 2017; Kleinberg et al., 2016). Cada diferença traz IC de 95% por bootstrap de 1000 repetições reamostrando pacientes. Se o IC inclui zero, a diferença **não está demonstrada**.

## 2. Limitações do dataset

- **Desbalanceamento:** 141 positivos em 3.185 imagens (4,43%). O teste tem 9 positivos de mulheres e 10 de homens.
- **Exclusão:** 2.421 de 5.606 imagens (outras doenças) foram excluídas. O modelo não foi testado na separação de cardiomegalia de outros achados.
- **Representatividade:** só existem as categorias M e F. A amostra original tem 44,1% de mulheres. A prevalência é 5,16% nas mulheres e 3,84% nos homens (Fisher, p = 0,083, não significativa a 5%), 5,71% em AP e 3,73% em PA, e 5,80% na faixa de 60 anos ou mais.
- **Rótulos:** extraídos dos laudos por processamento de linguagem natural (Wang et al., 2017), sem validação clínica independente. Erros podem afetar os grupos de forma desigual.

## 3. Resultados por sexo (diferença F menos M)

**ResNet50** (limiar 0,35; positivos acertados: F 8/9, M 9/10):

| Métrica | F | M | Diferença F - M | IC 95% | Leitura |
|---|---|---|---|---|---|
| taxa de sinalização | 0,325 | 0,373 | -0,048 | [-0,142 a 0,046] | diferença não demonstrada |
| recall | 0,889 | 0,900 | -0,011 | [-0,301 a 0,573] | diferença não demonstrada |
| falsos positivos | 0,297 | 0,351 | -0,054 | [-0,145 a 0,032] | diferença não demonstrada |
| precisão | 0,127 | 0,096 | 0,031 | [-0,094 a 0,153] | diferença não demonstrada |
| AUC-ROC | 0,843 | 0,855 | -0,013 | [-0,135 a 0,243] | diferença não demonstrada |

Nenhuma diferença demonstrada, o que não prova igualdade: com cerca de 10 positivos por grupo, o IC da diferença de recall é [-0,301 a 0,573].

**CNN simples** (limiar 0,79; positivos acertados: F 1/9, M 5/10): duas métricas excluem zero. A taxa de falsos positivos é 15,1% nas mulheres e 7,0% nos homens (diferença 0,081, IC [0,023 a 0,142]). A AUC-ROC é 0,482 nas mulheres e 0,809 nos homens (diferença -0,327, IC [-0,496 a -0,099]). Foram 10 comparações sem correção para múltiplos testes, e 2 excluem zero: são hipóteses para investigar com mais dados.

## 4. Projeção da radiografia e faixa etária

O Grad-CAM de um falso positivo (Notebook 3) mostrou uma radiografia portátil em AP. A razão cardiotorácica só é confiável em PA (PubMed 22065900) e a passagem de PA para AP amplia a silhueta cardíaca (PubMed 2966252). Hipótese: o modelo reage ao tipo de exame. Teste: taxa de falsos positivos da ResNet50 entre as imagens **sem achados** do teste.

| Projeção | Imagens | Sem achados | Falsos positivos | Taxa de falsos positivos (IC 95% de Wilson) | Positivos acertados |
|---|---|---|---|---|---|
| PA | 306 | 298 | 77 | 25,8% [21,2% a 31,1%] | 6/8 |
| AP | 140 | 129 | 63 | 48,8% [40,4% a 57,4%] | 11/11 |

A taxa é mais que o dobro em AP (Fisher, p < 0,001), o que sustenta a hipótese. Ressalva: a prevalência também é maior em AP, então parte do efeito pode refletir uma correlação real entre projeção e rótulo. Por faixa etária, a taxa cresce de 28,7% (<40) para 39,0% (60+), mas os intervalos se sobrepõem e a diferença não está demonstrada.

## 5. Mitigação experimental: limiares por sexo

Limiares por sexo, escolhidos na validação para igualar a taxa de sinalização de cada grupo à taxa geral (não se iguala o recall: a validação tem só 5 homens positivos). Na CNN, a diferença de falsos positivos cai de 0,081 para 0,011 (IC inclui zero), sem mudar os positivos sinalizados (6 para 6 de 19). Na ResNet50 os limiares por sexo saem iguais ao limiar único (0,350 e 0,350, contra 0,35) e nada muda. É um experimento, não uma recomendação: o mesmo escore passaria a significar coisas diferentes por grupo, com custos éticos e possíveis restrições legais em contexto clínico.

## 6. Implicações éticas e recomendações

- **Alertas falsos:** a ResNet50 sinaliza 35,2% das imagens do teste com precisão de 0,108. Em uso real, a maior parte dos alertas seria falsa (exames desnecessários, fadiga de alerta), e 2 de 19 casos ficariam sem alerta.
- **Ausência de diferença demonstrada não é equidade comprovada.** O teste tem poder baixo para comparar grupos de cerca de 10 positivos.
- **Confusor de projeção:** AP é a projeção das radiografias portáteis (PubMed 22065900). Um modelo que reage a ela pode sinalizar mais pacientes por contexto de atendimento, e não por cardiomegalia. É hipótese, não foi medido.
- **Sexo binário:** raça, etnia e condição socioeconômica não existem no dado e não puderam ser avaliadas.

**Recomendações:** (1) não usar o modelo em decisão clínica; (2) retreinar com balanceamento por projeção, ou restringir a PA, e repetir a medida; (3) ampliar os positivos com o dataset completo do NIH e usar validação cruzada por paciente; (4) reportar métricas por grupo com IC a cada versão, junto da ficha do modelo; (5) calibrar as pontuações e exigir revisão humana de toda imagem sinalizada; (6) validar em dados de outra instituição.

## 7. Limitações desta análise

Uma única divisão dos dados e uma única execução de cada modelo, com variação conhecida entre execuções e entre CPU e GPU. Poucos positivos por grupo. Análise limitada às variáveis que o dataset registra.

**Referências:** Wang X. et al. (2017), *ChestX-ray8*, IEEE CVPR ([arXiv:1705.02315](https://arxiv.org/abs/1705.02315)). Chouldechova A. (2017), *Fair prediction with disparate impact*. Kleinberg J., Mullainathan S., Raghavan M. (2016), *Inherent trade-offs in the fair determination of risk scores*. [PubMed 22065900](https://pubmed.ncbi.nlm.nih.gov/22065900/). [PubMed 2966252](https://pubmed.ncbi.nlm.nih.gov/2966252/).

*Projeto acadêmico. Nada neste relatório produz diagnóstico nem deve apoiar decisão clínica.*
