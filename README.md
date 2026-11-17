# Detector de Sementes de Abóbora

Projeto acadêmico de **processamento digital de imagens** para **detectar, contar e medir sementes de abóbora** (*pumpkin seeds*) em fotografias, utilizando Python, OpenCV e NumPy.

## 1. Contexto e objetivo

- **Tema sorteado:** Tema 1 — Inspeção e quantificação de grãos e sementes.
- **Combinação:** 3 — Semente de abóbora (*pumpkin seeds*).
- **Objetivo da aplicação:** identificar regiões correspondentes às sementes, contabilizá-las e extrair medidas a partir de imagens digitais.

A solução utiliza técnicas clássicas de processamento de imagens e implementa um algoritmo próprio de **busca em largura (Breadth-First Search — BFS)** para identificar componentes conectados na máscara binária.

## 2. Tecnologias utilizadas

- **Python:** linguagem principal.
- **OpenCV (`cv2`):** leitura, transformação e visualização de imagens; filtros e operações morfológicas.
- **NumPy:** representação de matrizes e construção dos limites e kernels utilizados no processamento.
- **`collections.deque`:** estrutura de fila usada na busca em largura.
- **`pathlib`:** construção de caminhos de arquivos.

As dependências Python estão registradas em `requirements.txt`.

## 3. Estrutura do projeto

```text
pumpkin-seed-detector-main/
├── data/
│   └── images/                  # Imagens disponíveis para o processamento
├── src/
│   ├── main.py                  # Executa o pipeline e mostra os resultados
│   ├── image_processing/
│   │   └── segmentation.py      # Pré-processamento e segmentação
│   ├── labeling/
│   │   └── labeling_methods.py  # BFS, identificação e medidas das regiões
│   └── reporting/
│       └── results_sheet.py     # Arquivo ainda sem implementação
├── requirements.txt             # Dependências
└── README.md
```

## 4. Funcionamento do pipeline

### Etapa 1 — Leitura da imagem

A imagem é carregada em cores com `cv2.imread()`. Na versão atual, o arquivo de entrada está definido diretamente em `src/main.py`:

```python
image_path = project_root / "data" / "images" / "pumpkin_0012.jpg"
```

Para analisar outra fotografia, é necessário alterar esse caminho no código.

### Etapa 2 — Pré-processamento e segmentação

O módulo `src/image_processing/segmentation.py` realiza as seguintes operações:

1. Converte a imagem do espaço de cores BGR para **HSV**.
2. Aplica um **filtro de mediana** com janela de tamanho `7` para atenuar pequenas irregularidades.
3. Aplica **limiarização por intervalo** (`cv2.inRange`) com os limites HSV `[18, 0, 100]` e `[255, 255, 255]`, produzindo uma máscara binária.
4. Executa **abertura morfológica** (`cv2.MORPH_OPEN`) com kernel `15 × 15` para reduzir regiões residuais na máscara.

Esses parâmetros estão definidos no código e podem ser ajustados experimentalmente.

### Etapa 3 — Identificação das regiões

O módulo `src/labeling/labeling_methods.py` percorre a máscara binária e utiliza uma implementação própria de **BFS** para reunir pixels brancos conectados em regiões.

São comparadas duas definições de vizinhança:

- **Conectividade 4:** considera os vizinhos acima, abaixo, à esquerda e à direita.
- **Conectividade 8:** considera esses quatro vizinhos e os quatro diagonais.

Cada região conectada é tratada pelo algoritmo como uma semente candidata. A contagem obtida, portanto, depende da qualidade da segmentação: sementes encostadas podem formar uma única região e resíduos podem formar regiões extras.

### Etapa 4 — Contagem e medição

Para cada região detectada, o programa calcula:

- **Área:** quantidade de pixels pertencentes à região (`seed_area`).
- **Dimensões:** extensão horizontal e vertical da caixa delimitadora, em pixels (`seed_height_width`). A função retorna primeiro a maior dimensão.
- **Proporção largura:altura:** dimensões da caixa delimitadora, no formato textual `x:y` (`seed_aspect_ratio`).
- **Delimitação visual:** desenho de um retângulo verde ao redor da região (`highlight_seeds`).

**Observação:** as medidas são expressas em **pixels**, não em milímetros ou centímetros. A conversão para dimensões físicas exigiria uma referência de escala ou calibração.

### Etapa 5 — Visualização

A implementação atual abre quatro janelas:

- `Original`: imagem de entrada.
- `Mascara`: imagem binária segmentada.
- `Areas 4`: regiões encontradas com conectividade 4.
- `Areas 8`: regiões encontradas com conectividade 8.

O terminal também exibe a quantidade de regiões identificadas em cada conectividade e as estatísticas referentes à conectividade 4.

## 5. Como instalar e executar

### Pré-requisitos

- Python 3 instalado.
- Um ambiente com suporte à abertura de janelas gráficas, necessário para `cv2.imshow()`.
- Acesso aos arquivos de imagem do projeto.

### Passo 1 — Obter o projeto

Baixe o repositório e extraia o conteúdo, ou clone o repositório, caso ele esteja publicado no GitHub. Abra um terminal na **pasta raiz** do projeto, onde está `requirements.txt`.

### Passo 2 — Criar e ativar um ambiente virtual (recomendado)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Passo 3 — Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

> **Atenção:** a instalação das versões exatas indicadas em `requirements.txt` ainda precisa ser validada no ambiente de execução. Se houver erro de versão ou compatibilidade, será necessário revisar as dependências antes da entrega.

### Passo 4 — Executar o programa

Na **pasta raiz do projeto**, execute:

```bash
python -m src.main
```

Em alguns ambientes Linux/macOS, pode ser necessário utilizar `python3 -m src.main`.

O programa processará `data/images/pumpkin_0012.jpg`, exibirá as contagens e medidas no terminal e abrirá as janelas de visualização. Pressione uma tecla com uma das janelas do OpenCV em foco para encerrá-las.

## 6. Base de dados e referências

### Base de dados obrigatória — Grain Detection Dataset

- **Nome:** Grain Detection Dataset
- **Página oficial:** [niru-5/manama_course_dataset_grain_detection (Hugging Face)](https://huggingface.co/datasets/niru-5/manama_course_dataset_grain_detection)
- **Conteúdo informado:** fotografias de grãos e sementes, divisões de **treino, validação e teste** e anotações no **formato COCO**.
- **Licença informada pela base:** [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) (Atribuição–NãoComercial 4.0 Internacional).
- **Classe de interesse neste trabalho:** `pumpkin seeds` (sementes de abóbora).

## 7. Integrantes

Amanda Silveira e João Vitor
Prof. Guilherme Chagas Kurtz
Unisinos - Ciência da Computação
