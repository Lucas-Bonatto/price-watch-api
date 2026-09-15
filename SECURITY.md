# Política de segurança

## Versões suportadas

A versão `0.2.x` recebe correções de segurança. Versões anteriores não possuem
as proteções atuais para conexões externas e não devem ser expostas à internet.

## Como reportar uma vulnerabilidade

Não abra uma issue pública contendo detalhes exploráveis. Envie o relato para
[lucas.jorchuabonatto@gmail.com](mailto:lucas.jorchuabonatto@gmail.com) com:

* descrição e impacto esperado;
* passos mínimos para reprodução;
* versão ou commit afetado;
* evidências que não contenham dados pessoais ou segredos.

O recebimento será confirmado antes que qualquer divulgação pública seja combinada.

## Modelo de segurança do scraper

O scraper opera com uma allowlist exata de hosts e recusa HTTP, portas não padrão,
credenciais na URL, IPs literais e resoluções DNS que incluam endereços não globais.
Todo redirecionamento é limitado e submetido novamente à mesma política.

A aplicação também limita o tipo e o tamanho das respostas e não herda proxies do
ambiente. Em produção, esses controles devem ser complementados por regras de egress
que bloqueiem redes internas e endpoints de metadata na infraestrutura.

As chaves, senhas e URLs privadas de produção nunca devem ser incluídas em relatos,
issues, logs ou commits.
