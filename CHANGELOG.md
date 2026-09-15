# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o
versionamento segue [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.2.0] - 2026-09-09

### Adicionado

* allowlist configurável de hosts externos;
* validação DNS para IPv4 e IPv6;
* testes de segurança para URLs, redirects e respostas HTTP;
* política de divulgação responsável em `SECURITY.md`;
* lint obrigatório no GitHub Actions;
* `httpx2` como cliente compatível com o `TestClient` atual do Starlette.

### Segurança

* bloqueio de IPs privados, locais, link-local, reservados e não roteáveis;
* revalidação manual de cada redirecionamento;
* bloqueio de credenciais, IPs literais, HTTP e portas não padrão;
* limite de três redirecionamentos e 2 MiB por resposta;
* restrição das respostas a HTML/XHTML;
* desativação de proxies herdados do ambiente.

## [0.1.0] - 2026-07-01

### Adicionado

* API inicial para produtos, histórico de preços e alertas;
* scraper de páginas de produtos;
* persistência SQLite e testes automatizados.
