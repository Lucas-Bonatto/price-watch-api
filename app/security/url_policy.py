import ipaddress
import os
import socket
from collections.abc import Callable, Iterable
from typing import Any
from urllib.parse import SplitResult, urlsplit


DEFAULT_ALLOWED_HOSTS = "books.toscrape.com"
ALLOWED_HOSTS_ENV = "PRICE_WATCH_ALLOWED_HOSTS"

Resolver = Callable[..., list[tuple[Any, ...]]]


class UnsafeUrlError(ValueError):
    """Indica que uma URL viola a política de acesso externo da aplicação."""


def get_allowed_hosts() -> frozenset[str]:
    """Carrega a allowlist exata de hosts a partir do ambiente."""
    configured_hosts = os.getenv(ALLOWED_HOSTS_ENV, DEFAULT_ALLOWED_HOSTS)
    hosts = {
        host.strip().lower().rstrip(".")
        for host in configured_hosts.split(",")
        if host.strip()
    }

    if not hosts:
        raise UnsafeUrlError("A lista de hosts permitidos não pode estar vazia.")

    return frozenset(hosts)


def validate_url_structure(
    url: str,
    *,
    allowed_hosts: Iterable[str] | None = None,
) -> SplitResult:
    """Valida protocolo, credenciais, porta e host sem realizar acesso à rede."""
    try:
        parsed_url = urlsplit(url)
        port = parsed_url.port
    except ValueError as error:
        raise UnsafeUrlError("A URL informada possui uma porta inválida.") from error

    if parsed_url.scheme.lower() != "https":
        raise UnsafeUrlError("Apenas URLs HTTPS são permitidas para monitoramento.")

    if parsed_url.username is not None or parsed_url.password is not None:
        raise UnsafeUrlError("URLs com credenciais embutidas não são permitidas.")

    hostname = (parsed_url.hostname or "").lower().rstrip(".")

    if not hostname:
        raise UnsafeUrlError("A URL precisa conter um host válido.")

    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        raise UnsafeUrlError("Endereços IP literais não são permitidos.")

    configured_hosts = get_allowed_hosts() if allowed_hosts is None else allowed_hosts
    normalized_allowed_hosts = {
        allowed_host.strip().lower().rstrip(".")
        for allowed_host in configured_hosts
        if allowed_host.strip()
    }

    if not normalized_allowed_hosts:
        raise UnsafeUrlError("A lista de hosts permitidos não pode estar vazia.")

    if hostname not in normalized_allowed_hosts:
        raise UnsafeUrlError(
            f"O host '{hostname}' não está autorizado para monitoramento."
        )

    if port not in (None, 443):
        raise UnsafeUrlError("Apenas a porta HTTPS padrão (443) é permitida.")

    return parsed_url


def validate_outbound_url(
    url: str,
    *,
    allowed_hosts: Iterable[str] | None = None,
    resolver: Resolver | None = None,
) -> None:
    """Rejeita destinos que não resolvam exclusivamente para IPs públicos."""
    parsed_url = validate_url_structure(url, allowed_hosts=allowed_hosts)
    hostname = parsed_url.hostname

    if hostname is None:
        raise UnsafeUrlError("A URL precisa conter um host válido.")

    resolve = resolver or socket.getaddrinfo

    try:
        address_info = resolve(
            hostname,
            443,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
    except OSError as error:
        raise UnsafeUrlError("Não foi possível resolver o host informado.") from error

    resolved_addresses: set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()

    for entry in address_info:
        socket_address = entry[4]
        raw_address = str(socket_address[0]).split("%", maxsplit=1)[0]

        try:
            resolved_addresses.add(ipaddress.ip_address(raw_address))
        except ValueError as error:
            raise UnsafeUrlError("O host retornou um endereço IP inválido.") from error

    if not resolved_addresses:
        raise UnsafeUrlError("O host não possui endereços IP acessíveis.")

    if any(not address.is_global for address in resolved_addresses):
        raise UnsafeUrlError(
            "O host resolve para uma rede privada, local ou não roteável."
        )
