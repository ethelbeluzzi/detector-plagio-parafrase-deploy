# Projeto de Comparação de Textos

Este projeto implementa um sistema para **comparar textos** por duas abordagens complementares:  
- **Léxica** – análise baseada em padrões de palavras (TF-IDF e n-gramas).  
- **Semântica** – análise baseada no significado (embeddings com `sentence-transformers`).  

O objetivo é combinar essas análises para obter uma avaliação robusta da similaridade textual, útil para detecção de plágio, identificação de paráfrases e comparação de conteúdos de domínio público.  

O projeto foi pensado para rodar **tanto localmente quanto via Docker**, garantindo que o ambiente seja reprodutível e que os resultados sejam consistentes.

---

## Seleção da Base de Comparação

Para compor a base pública do projeto, optou-se por utilizar textos brutos obtidos da **Wikipédia em português**, por meio de um script automatizado que consulta a API pública da plataforma.  

O ponto de partida foram temas relacionados aos assuntos das últimas redações do ENEM — como questões sociais, culturais e políticas. A partir desses artigos iniciais (*seeds*), o script percorreu links internos para ampliar o conjunto até atingir aproximadamente 200 documentos (neste caso, 174).  

Essa abordagem garante:  
- **Diversidade temática** e relevância educacional.  
- **Conformidade legal**, utilizando apenas conteúdo de domínio público.  
- **Escopo controlado**, atendendo ao requisito de uma base pequena (100–200 textos).

**Exemplos de seeds utilizados:**  
Trabalho doméstico, Trabalho de cuidado, Mulheres no Brasil, Igualdade de gênero, Povos e comunidades tradicionais, Povos indígenas do Brasil, Quilombolas, Registro civil, Cidadania, Direitos humanos no Brasil, Estigma associado às doenças mentais, Saúde mental no Brasil, Suicídio, Depressão, Democratização do acesso ao cinema, Cinema do Brasil, Política cultural do Brasil, Dados pessoais, Privacidade na Internet, Proteção de dados no Brasil, Lei Geral de Proteção de Dados, Educação de surdos, Língua brasileira de sinais, Acessibilidade, Intolerância religiosa no Brasil, Liberdade religiosa, Violência contra a mulher no Brasil, Lei Maria da Penha, Publicidade infantil, Direito do consumidor no Brasil, Lei Seca, Álcool e direção, Imigração no Brasil, Refugiados no Brasil, Redes sociais, Cultura digital, Desinformação, Fake news, Democracia no Brasil, Participação política, Mobilidade urbana, Meio ambiente no Brasil, Sustentabilidade, Racismo no Brasil, Inclusão social, Desigualdade social no Brasil, Educação no Brasil, Bullying, Trabalho infantil no Brasil, Ética.

---

## Estrutura de Pastas

app/                 
data/                
  indexes/
    lexical/
    semantic/
  raw/
src/                 
  compare_lexical.py
  compare_semantic.py
  combine_scores.py
  compare_service.py
  config.py
  io_utils.py
  pipeline_build_index.py
  preprocess.py
tests/               
Dockerfile


---

## Detalhamento e motivos da organização

- **app/** – Contém a interface Streamlit, que permite interação direta com o usuário para envio de textos e visualização dos resultados. Manter a interface separada da lógica garante que alterações visuais ou de usabilidade não impactem o núcleo de processamento.
  
- **data/** – Estrutura para persistência de dados:  
  - **raw/** preserva o corpus original para que o pipeline possa ser reexecutado sem depender de fontes externas.  
  - **indexes/lexical/** e **indexes/semantic/** guardam índices prontos, evitando recomputações custosas e acelerando a inicialização, especialmente em ambientes Docker.
  
- **src/** – Código-fonte principal, modularizado para facilitar manutenção, testes e substituição de componentes:
  - **`compare_lexical.py`** – Implementa a comparação léxica com TF-IDF e similaridade do cosseno sobre janelas de texto, buscando rapidez e interpretabilidade.
  - **`compare_semantic.py`** – Executa a comparação semântica usando embeddings normalizados, captando similaridades mesmo quando o vocabulário difere; modelo carregado sob demanda com cache para eficiência.
  - **`combine_scores.py`** – Une resultados léxicos e semânticos, aplica pesos configuráveis e thresholds para classificar correspondências.
  - **`compare_service.py`** – Orquestra o pipeline completo, do fracionamento do texto até a geração do resultado final estruturado.
  - **`config.py`** – Centraliza parâmetros de configuração, permitindo ajustes por variáveis de ambiente sem modificar código.
  - **`io_utils.py`** – Padroniza leitura e escrita de dados e índices, garantindo compatibilidade entre etapas do pipeline.
  - **`pipeline_build_index.py`** – Responsável por criar os índices a partir do corpus, aplicando janelas deslizantes para aumentar a precisão das correspondências.
  - **`preprocess.py`** – Cuida da segmentação de texto, criação de janelas e extensão de contexto.
  
- **tests/** – Contém testes unitários e de integração que asseguram a confiabilidade do sistema em cada atualização.  
- **Dockerfile** – Define um ambiente reprodutível, reduzindo diferenças de comportamento entre máquinas locais e pipelines de CI/CD.

---

## Persistência e Reprodutibilidade

A organização em `data/` foi projetada para **evitar retrabalho** e permitir reuso eficiente dos resultados mais custosos (índices léxicos e semânticos).  
Essa persistência garante inicialização rápida e resultados idênticos, seja em execução local ou via Docker.

---

## Testes Automatizados

Os testes seguem princípios de **isolamento**, **eficiência** e **clareza semântica**:  
- Execução determinística, sem dependências externas.  
- Uso de *mocks* para simular partes pesadas do processamento.  
- Tempo de execução reduzido, viabilizando integração contínua.

**Cobertura por módulo:**  
- `compare_lexical` / `compare_semantic` – Verificam cálculos de similaridade e ranqueamento, inclusive com entradas vazias.  
- `combine_scores` – Testa a fusão ponderada de scores e aplicação correta das classificações.  
- `pipeline_build_index` / `io_utils` – Garante que a indexação e a persistência sejam reprodutíveis e seguras.  
- `preprocess` – Valida segmentação e manipulação de janelas, incluindo casos de borda.  
- `config` – Testa a leitura de parâmetros e preservação de valores padrão.  
- `compare_service` – Avalia a integração de todas as etapas e a estrutura final do retorno.

O **GitHub Actions** executa automaticamente toda a suíte de testes a cada push, bloqueando implantações se houver falhas.

---

## Otimização da Imagem Docker

Para manter a imagem leve e rápida:  
- **`python:3.11-slim`** – Reduz significativamente o tamanho em relação à imagem padrão.  
- **Build multiestágio** – Ferramentas de compilação ficam apenas no estágio de build.  
- **Instalação mínima** – Uso de `--no-install-recommends` e limpeza do cache do `apt`.  
- **PyTorch CPU-only** – Elimina dependências de GPU, reduzindo peso e complexidade.  
- **Sem modelos embutidos** – O modelo é baixado no primeiro uso.  
- **Variáveis otimizadas** – `PIP_NO_CACHE_DIR=1` e `HF_HOME` configurado para cache previsível.

---

## Interface com Streamlit

O arquivo `app/streamlit_app.py` implementa a interface para envio de textos e visualização dos resultados:  
- Destaques visuais para plágio literal e paráfrase.  
- Tabelas com scores e métricas detalhadas.  
- Contexto diretamente no texto analisado.  

O Streamlit facilita a execução local e em Docker, mantendo separação entre lógica (`src/`) e apresentação.
