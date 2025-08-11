Seleção da Base de Comparação
Para compor a base pública do projeto, optamos por utilizar textos brutos obtidos da Wikipédia em português, por meio de um script automatizado que consulta a API pública da plataforma. O ponto de partida foram temas relacionados aos assuntos das últimas redações do ENEM — como questões sociais, culturais e políticas — e, a partir desses artigos iniciais (seeds), o script percorreu links internos para ampliar o conjunto até atingir aproximadamente 200 documentos (no caso, 174). Essa abordagem garante diversidade temática e relevância educacional, ao mesmo tempo em que assegura que o conteúdo seja de domínio público e acessível, atendendo aos requisitos do case para uma base pequena (100–200 textos) de documentos de livre utilização.


## Testes Automatizados
Cada função principal tem pelo menos um teste, seguindo boas práticas de **isolamento**, **rapidez** e **clareza**.  
Isso significa que cada teste foi pensado para rodar de forma independente, sem depender de arquivos externos, conexões de rede ou estado compartilhado; para executar rapidamente, usando dados pequenos e simulando partes pesadas com *mocks*; e para ser claro, com nomes e cenários que deixam explícito qual comportamento está sendo validado.

No **GitHub Actions**, é possível verificar que todos os testes passam com sucesso, garantindo a confiabilidade do código.

### Estrutura dos testes
- **compare_lexical / compare_semantic** – uso de *mocks* e dados em memória para evitar dependências externas.  
- **combine_scores** – verificação de ordenação por `score_final` sem depender de `set`, garantindo consistência no CI.  
- **pipeline_build_index / io_utils** – uso de `tmp_path` e *mocks* para I/O seguro.  
- **preprocess** – cobertura de casos de borda na manipulação de texto.  
- **config** – validação de variáveis customizadas e *defaults*.  
- **compare_service** – teste de orquestração com dependências *mockadas* para retorno determinístico.  
