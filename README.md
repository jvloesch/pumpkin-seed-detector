# Detector de Sementes de Abóbora 

**Trabalho acadêmico — Processamento Digital de Imagens**  
**Curso:** Ciência da Computação — Unisinos  
**Professor:** Guilherme Chagas Kurtz  
**Integrantes:** Amanda Silveira e João Vitor

## 1. Sobre o projeto

Este projeto desenvolve uma solução de **inspeção e quantificação de sementes de abóbora** em fotografias completas. Utiliza técnicas clássicas de processamento de imagens com **Python, OpenCV e NumPy** para segmentar as regiões de interesse, identificar componentes conectados, contar possíveis sementes e calcular medidas em pixels.

- **Tema 1:** Inspeção e quantificação de grãos e sementes.
- **Combinação 3:** Semente de abóbora (*pumpkin seeds*).
- **Classe analisada:** `pumpkin` nas anotações COCO disponibilizadas no projeto.
- **Técnica algorítmica implementada pelo grupo:** busca em largura (**BFS — Breadth-First Search**) para rotulagem de componentes conectados.

O projeto inclui uma rotina de visualização individual e uma rotina de **avaliação em lote**, com comparação de quatro configurações, anotações de referência e geração de resultados em JSON.

## 2. Base de dados

**Grain Detection Dataset**  
**Fonte:** [Hugging Face — niru-5/manama_course_dataset_grain_detection](https://huggingface.co/datasets/niru-5/manama_course_dataset_grain_detection)  
**Conteúdo:** fotografias de grãos e sementes, divisões de treino, validação e teste e anotações no formato **COCO**.  
**Licença informada pela base:** [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — Atribuição–NãoComercial 4.0 Internacional.

O trabalho utiliza **fotografias completas de validação e teste e suas respectivas anotações**, mantendo a localização dos objetos nas imagens originais. **Recortes anotados não substituem a detecção nas fotografias completas.**

No pacote analisado, a organização é:

| Divisão | Arquivo de anotação | Fotografias | Objetos anotados |
|---|---|---:|---:|
| Validação | `data/annotations/val_photos_pumpkin_only.json` | 14 | 395 |
| Teste | `data/annotations/test_photos_pumpkin_only.json` | 15 | 432 |
| **Total** | — | **29** | **827** |

As **29 fotografias** correspondentes encontram-se em `data/images/`. A categoria registrada nos JSONs de anotação é `pumpkin`. Os números acima representam as **anotações de referência da base**, não resultados de acerto do detector.

> **Nota metodológica:** os arquivos de validação e teste estão identificados separadamente. O script de avaliação atual processa todas as imagens da pasta e calcula métricas agregadas; ele **não separa automaticamente os resultados por divisão**, nem implementa um procedimento de ajuste de parâmetros restrito à validação.

## 3. Tecnologias utilizadas

- **Python 3:** implementação da aplicação.
- **OpenCV (`cv2`):** leitura de imagens, conversão de cores, filtro de mediana, limiarização, morfologia e visualização.
- **NumPy:** matrizes, limites HSV e kernels morfológicos.
- **`collections.deque`:** fila utilizada no algoritmo BFS.
- **Bibliotecas padrão `json`, `pathlib`, `time`, `statistics` e `random`:** arquivos, avaliação, medição de tempo e seleção de imagem.

Não são utilizados modelos de inteligência artificial, redes neurais ou serviços externos de inferência.

## 4. Estrutura do repositório

```text
pumpkin-seed-detector-main/
├── data/
│   ├── images/                           # 29 fotografias completas
│   └── annotations/
│       ├── val_photos_pumpkin_only.json  # Referência COCO: validação
│       └── test_photos_pumpkin_only.json # Referência COCO: teste
├── src/
│   ├── main.py                           # Visualização de uma imagem aleatória
│   ├── testing.py                        # Avaliação em lote e saída JSON
│   ├── image_processing/
│   │   └── segmentation.py               # Pré-processamento e segmentação
│   ├── labeling/
│   │   └── labeling_methods.py           # BFS, contagem, medidas e desenho
│   └── reporting/
│       └── results_sheet.py              # Comparação com COCO e métricas
├── requirements.txt
└── README.md
```

Após executar os testes, é criado `data/annotations/seed_statistics.json` com os resultados calculados.

## 5. Pipeline de processamento

O fluxo aplicado a cada fotografia é:

**Imagem original → Conversão BGR/HSV → Filtro de mediana → Limiarização HSV → Abertura morfológica → BFS (4 ou 8 vizinhos) → Contagem e medidas.**

### 5.1. Pré-processamento e segmentação

O arquivo `src/image_processing/segmentation.py` aplica:

1. **Conversão BGR → HSV**, para trabalhar com componentes de cor.
2. **Filtro de mediana** com tamanho `7`, reduzindo pequenas irregularidades visuais.
3. **Limiarização por intervalo** com `cv2.inRange` e limites `[18, 0, 100]` e `[255, 255, 255]`, produzindo uma máscara binária.
4. **Abertura morfológica** (`cv2.MORPH_OPEN`), para reduzir regiões indesejadas.

A investigação compara duas configurações de abertura morfológica:

| Configuração | Kernel de abertura | Demais etapas |
|---|---|---|
| **Pipeline A** (`pipeline=0`) | `15 × 15` | Iguais às do Pipeline B |
| **Pipeline B** (`pipeline=1`) | `11 × 11` | Iguais às do Pipeline A |

Os parâmetros ficam explícitos no código. Kernels diferentes podem alterar a preservação de regiões pequenas e a eliminação de resíduos.

### 5.2. Identificação com BFS

O arquivo `src/labeling/labeling_methods.py` implementa a **busca em largura (BFS)**, percorrendo os pixels brancos da máscara para formar conjuntos de pixels conectados.

- **Conectividade 4** (`connectivity=0`): vizinhos superior, inferior, esquerdo e direito.
- **Conectividade 8** (`connectivity=1`): os quatro anteriores e os quatro vizinhos diagonais.

Cada região conectada é tratada como **candidata a semente**. Essa aproximação pode produzir erros quando sementes próximas se unem em uma única região ou quando parte do fundo é segmentada.

### 5.3. Contagem e medidas

Para cada região encontrada, são obtidos:

- **Área (`area`):** quantidade de pixels da região.
- **Altura e largura (`height`, `width`):** dimensões derivadas da caixa delimitadora. A função atual retorna a **maior dimensão primeiro**, independentemente da orientação original do objeto.
- **Proporção (`aspect_ratio`):** relação textual entre as dimensões horizontal e vertical da caixa, no formato `largura:altura`.
- **Contagem (`total_seeds`):** número de componentes encontrados na imagem.

As medidas são dadas em **pixels**, e não em unidades físicas (mm ou cm). Não há calibração de escala implementada.

## 6. Como instalar e executar

### Pré-requisitos

- Python 3 instalado.
- Terminal aberto na **pasta raiz do projeto**.
- Para a visualização de `src/main.py`, ambiente que permita abrir janelas do OpenCV (`cv2.imshow`).

### 6.1. Criar um ambiente virtual (recomendado)

**Windows — PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 6.2. Instalar dependências

O projeto contém `requirements.txt` para registrar as dependências. **Atenção:** no ZIP recebido, ele fixa `numpy==2.5.4` e `opencv-python==5.0.0.93`; a disponibilidade/compatibilidade dessas versões não foi validada. Caso `pip install -r requirements.txt` falhe, utilize a instalação sem essas versões fixas:

```bash
python -m pip install numpy opencv-python
```

Para uma entrega reproduzível, recomenda-se corrigir e testar as versões de `requirements.txt` no ambiente usado pelo grupo.

### 6.3. Executar a demonstração visual

```bash
python -m src.main
```

O programa seleciona **uma imagem aleatória** de `data/images/`, exibe no terminal a contagem e as medidas com conectividades 4 e 8 e abre quatro janelas: `Original`, `Mascara`, `Areas 4` e `Areas 8`.

O script `main.py` utiliza **Pipeline A** por padrão. Para visualizar o Pipeline B, alterar `segment_image(image, 0)` para `segment_image(image, 1)` no arquivo. Para fechar as janelas, pressione uma tecla com uma janela do OpenCV em foco.

### 6.4. Executar a avaliação automática em lote

```bash
python -m src.testing
```

Esse comando:

1. Percorre automaticamente as imagens de `data/images/`.
2. Executa **Pipeline A e B**, cada um com conectividade **4 e 8**.
3. Calcula contagem e medidas de todas as regiões detectadas.
4. Salva as informações em `data/annotations/seed_statistics.json`.
5. Compara as contagens com as anotações COCO e imprime tabela comparativa, totais e MAE no terminal.
6. Mostra o tempo total decorrido da rotina de processamento e avaliação.

Também é possível imprimir novamente a comparação a partir do JSON salvo, sem processar as fotografias outra vez:

```bash
python -m src.reporting.results_sheet
```

> O relatório pode ser exibido mais de uma vez por esse último comando devido à duplicação do bloco `if __name__ == "__main__"` no final do arquivo `results_sheet.py`. Isso não altera os cálculos.

## 7. Investigação experimental

### Pergunta investigada

**Como a alteração do tamanho do kernel morfológico (15×15 e 11×11) e da conectividade utilizada na BFS (4 ou 8) afeta a contagem das sementes de abóbora?**

A implementação compara quatro configurações:

| Variante | Segmentação | Identificação |
|---|---|---|
| A-4 | Pipeline A — kernel 15×15 | Conectividade 4 |
| A-8 | Pipeline A — kernel 15×15 | Conectividade 8 |
| B-4 | Pipeline B — kernel 11×11 | Conectividade 4 |
| B-8 | Pipeline B — kernel 11×11 | Conectividade 8 |

### Dados de referência

As contagens reais são obtidas dos arquivos de anotação COCO por meio da relação entre `images[].id` e `annotations[].image_id`. Cada anotação vinculada à imagem é contabilizada na quantidade esperada de sementes.

### Métricas

- **Contagem esperada:** número de objetos anotados na base para cada fotografia.
- **Contagem detectada:** quantidade de componentes retornados pelo algoritmo.
- **Diferença de contagem:** `detectado - esperado`.
- **Erro absoluto:** `abs(detectado - esperado)`.
- **MAE (Mean Absolute Error):** média dos erros absolutos por fotografia.
- **Tempo total:** duração da rotina de avaliação em lote, medida com `time.perf_counter()`.

A métrica MAE de contagem é definida por:

\[
MAE = \frac{1}{N} \sum_{i=1}^{N} |\hat{c}_i - c_i|
\]

em que `N` é a quantidade de imagens comparadas, `ĉᵢ` é a contagem automática e `cᵢ` é a contagem anotada.

**Importante:** MAE de contagem não mede, por si só, precisão de localização ou correspondência individual entre caixas detectadas e anotações COCO; erros de omissão e excesso podem se compensar na contagem total. O tempo registrado corresponde à **execução agregada dos testes**, não a tempos individuais por fotografia ou por configuração.

### Resultados

Os resultados numéricos são produzidos ao executar `python -m src.testing` e são impressos no terminal; as contagens e medidas de cada variante ficam no JSON gerado. **Não foram incluídos neste README valores de desempenho sem uma execução de avaliação confirmada.**

### Limitações e situações de falha

- Sementes encostadas ou sobrepostas podem ser contadas como um único componente.
- Regiões do fundo com características dentro do intervalo HSV podem gerar falsos positivos.
- A morfologia pode remover partes de sementes ou componentes menores.
- Alterações de iluminação, cor, contraste e perspectiva podem influenciar a máscara.
- O código compara contagens, mas ainda não calcula métricas de detecção baseadas em correspondência espacial (como IoU, precisão e revocação).

## 8. Arquivos de saída

**`data/annotations/seed_statistics.json`** é gerado pelo script de testes e organiza os resultados por fotografia, com os campos:

- `file_name`: nome do arquivo de imagem;
- `pipeline_a_connectivity_4`, `pipeline_a_connectivity_8`, `pipeline_b_connectivity_4` e `pipeline_b_connectivity_8`: resultados das quatro variantes;
- `total_seeds`: total de regiões detectadas;
- `statistics`: lista com `height`, `width`, `area` e `aspect_ratio` para cada região.

O programa também imprime no terminal uma **tabela de comparação** com contagens esperadas e detectadas, diferenças, totais e MAE. **O projeto não exporta CSV nem salva automaticamente as imagens com caixas desenhadas** na rotina de testes presente no ZIP.

## 9. Referências

1. **Grain Detection Dataset** — `niru-5/manama_course_dataset_grain_detection`. Hugging Face. Disponível em: https://huggingface.co/datasets/niru-5/manama_course_dataset_grain_detection
2. **OpenCV** — documentação oficial. https://docs.opencv.org/
3. **NumPy** — documentação oficial. https://numpy.org/doc/
4. **Creative Commons** — licença CC BY-NC 4.0. https://creativecommons.org/licenses/by-nc/4.0/

---

**Contexto acadêmico:** solução desenvolvida para a disciplina de Processamento Gráfico, com foco em técnicas clássicas de segmentação, rotulagem, medição e avaliação experimental.
