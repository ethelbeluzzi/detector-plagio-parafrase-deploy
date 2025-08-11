Seleção da Base de Comparação
Para compor a base pública do projeto, optamos por utilizar textos brutos obtidos da Wikipédia em português, por meio de um script automatizado que consulta a API pública da plataforma. O ponto de partida foram temas relacionados aos assuntos das últimas redações do ENEM — como questões sociais, culturais e políticas — e, a partir desses artigos iniciais (seeds), o script percorreu links internos para ampliar o conjunto até atingir aproximadamente 200 documentos (no caso, 174). Essa abordagem garante diversidade temática e relevância educacional, ao mesmo tempo em que assegura que o conteúdo seja de domínio público e acessível, atendendo aos requisitos do case para uma base pequena (100–200 textos) de documentos de livre utilização.


## Testes Automatizados

O projeto possui cobertura sistemática das funções nucleares, com testes desenhados segundo princípios de **isolamento**, **eficiência** e **clareza semântica**.  
Cada teste é concebido para executar de forma determinística, sem dependências externas de I/O, rede ou estado global, utilizando *fixtures* controladas e *mocks* para simular componentes de maior custo computacional.  
O conjunto é otimizado para execução rápida, mantendo a legibilidade e a rastreabilidade do comportamento validado.

A execução contínua no **GitHub Actions** confirma, em cada *pipeline*, que todas as verificações são aprovadas, sustentando a confiabilidade do código em produção.

### Estrutura dos testes
- **compare_lexical / compare_semantic** – garantem que os cálculos de similaridade e o ranqueamento de resultados funcionem corretamente, respeitando parâmetros como `top_n` e `k` e tratando entradas vazias.  
- **combine_scores** – valida a correta combinação ponderada de scores léxicos e semânticos, bem como a atribuição dos rótulos de classificação segundo as regras definidas.  
- **pipeline_build_index / io_utils** – asseguram que o processo de indexação e persistência gere as estruturas esperadas de forma segura e reprodutível, sem efeitos colaterais no sistema de arquivos.  
- **preprocess** – confirma a segmentação e manipulação textual, cobrindo cenários típicos e casos de borda para janelas deslizantes e margens de contexto.  
- **config** – garante a correta leitura e aplicação de parâmetros vindos de variáveis de ambiente, preservando *defaults* quando necessário.  
- **compare_service** – valida a orquestração completa do fluxo de comparação, verificando a integração entre os módulos e a estrutura final do retorno.

## Dockerfile
- Este projeto usa estratégias para manter a imagem Docker **leve** com `python:3.11-slim`:

- **Imagem base enxuta**: `python:3.11-slim` reduz centenas de MB em relação à imagem padrão.
- **Build multiestágio**: ferramentas de compilação ficam só no estágio de build, não no runtime.
- **Instalação mínima**: `--no-install-recommends` e limpeza do cache do apt.
- **PyTorch CPU-only**: evita dependências GPU pesadas.
- **Sem modelos embutidos**: o Hugging Face baixa no primeiro uso, mantendo a imagem pequena.
- **Variáveis otimizadas**: `PIP_NO_CACHE_DIR=1` e `HF_HOME` para cache previsível.

