# Auditoria visual — Radar de Preços

## Contexto da comparação

- Referência aprovada: `C:\Users\Usuario\.codex\generated_images\01a085f1-0825-7083-ac09-5a6b1e8c0d23\exec-d43a0a28-1207-4fa9-b4ea-f764ee1b380f.png`
- Referência: 1487 × 1058 px.
- Implementação desktop: `docs/design/implementation-desktop.png` (1473 × 1045 px).
- Implementação móvel: `docs/design/implementation-mobile.png` (375 × 812 px).
- Estado avaliado: primeira carga, demonstração somente para leitura, dados reais carregados pelos endpoints locais.
- Data da avaliação: 16 de setembro de 2026.

## Comparação completa

### Estrutura e hierarquia

- Cabeçalho, marca, navegação, indicador de disponibilidade, hero em duas colunas, narrativa de dados, prova de endpoint, capacidades e rodapé seguem a composição da referência.
- O título editorial, o contraste entre tipografia serifada e sans-serif e os acentos em azul e coral foram preservados.
- A implementação adapta o conteúdo ao espaço real do navegador sem sobreposição ou corte de controles.

### Dados e comportamento

- O gráfico usa os preços reais retornados por `/products`, `/products/{id}/history` e `/products/{id}/alert`.
- A meta exibida é R$ 40,00 e o último preço é R$ 39,99, coerentes com os dados semeados da demonstração.
- O estado “API online” depende de `/health`.
- O botão “Copiar” foi exercitado e mudou para o estado “Copiado”.
- A documentação permanece disponível em `/docs`; as informações básicas em JSON foram preservadas em `/api`.

### Responsividade e acessibilidade

- Em 375 × 812 px, a interface reorganiza hero, ações, indicadores, gráfico e capacidades em uma coluna.
- Medição móvel: `scrollWidth = clientWidth = 375`, sem rolagem horizontal.
- A página possui link de salto, regiões nomeadas, hierarquia de títulos, rótulo para o gráfico, foco visível e suporte a redução de movimento.

## Região focal

A região focal comparada foi o conjunto hero + gráfico + prova de endpoint. Ela mantém a relação visual dominante da referência: proposta de valor à esquerda e evidência técnica/dados à direita.

## Histórico de correções

1. O título principal quebrava em quatro linhas; a escala tipográfica foi reduzida para recuperar as três linhas da referência.
2. O título “Do monitoramento à decisão.” quebrava em duas linhas; o rótulo da seção foi reposicionado para liberar a largura necessária.
3. A prova do endpoint foi alinhada ao contrato real: agora mostra um trecho válido da lista de históricos, incluindo `id`, `product_id`, `price`, `available` e `checked_at`.
4. Os botões principais foram ajustados para permanecer lado a lado no desktop e empilhados no celular.
5. A composição foi revalidada no desktop e em viewport móvel após as correções.

## Resultado

Não há pendências P0, P1 ou P2. A diferença de quantidade de pontos em relação ao mockup é deliberada: a interface usa o conjunto real da API em vez de dados ilustrativos inventados.

final result: passed
