Seleção da Base de Comparação
Para compor a base pública do projeto, optamos por utilizar textos brutos obtidos da Wikipédia em português, por meio de um script automatizado que consulta a API pública da plataforma. O ponto de partida foram temas relacionados aos assuntos das últimas redações do ENEM — como questões sociais, culturais e políticas — e, a partir desses artigos iniciais (seeds), o script percorreu links internos para ampliar o conjunto até atingir aproximadamente 200 documentos (no caso, 174). Essa abordagem garante diversidade temática e relevância educacional, ao mesmo tempo em que assegura que o conteúdo seja de domínio público e acessível, atendendo aos requisitos do case para uma base pequena (100–200 textos) de documentos de livre utilização.


## Testes Automatizados
O projeto possui cobertura sistemática das funções nucleares, com testes desenhados segundo princípios de **isolamento**, **eficiência** e **clareza semântica**.  
Cada teste é concebido para executar de forma determinística, sem dependências externas de I/O, rede ou estado global, utilizando *fixtures* controladas e *mocks* para simular componentes de maior custo computacional.  
O conjunto é otimizado para execução rápida, mantendo a legibilidade e a rastreabilidade do comportamento validado.

A execução contínua no **GitHub Actions** confirma, em cada *pipeline*, que todas as verificações são aprovadas, sustentando a confiabilidade do código em produção.

### Estrutura dos testes
- **compare_lexical / compare_semantic** – valida algoritmos de similaridade com *mocks* e dados sintéticos, assegurando isolamento de modelos externos.  
- **combine_scores** – verifica a lógica de agregação e classificação, eliminando não determinismo decorrente de estruturas não ordenadas.  
- **pipeline_build_index / io_utils** – avalia fluxos de indexação e persistência com diretórios temporários e *mocks* de armazenamento, garantindo segurança e reprodutibilidade.  
- **preprocess** – assegura a correta segmentação e manipulação textual, cobrindo cenários limítrofes.  
- **config** – valida a carga de parâmetros a partir de variáveis de ambiente, confirmando a aplicação de *defaults*.  
- **compare_service** – testa o fluxo orquestrado de comparação com simulações controladas de todos os módulos dependentes, assegurando integridade estrutural no retorno.  

