import socket

import pytest

from app.security.url_policy import (
    UnsafeUrlError,
    validate_outbound_url,
    validate_url_structure,
)


def resolver_for(*addresses: str):
    def resolve(host, port, **kwargs):
        del host, kwargs
        return [
            (
                socket.AF_INET6 if ":" in address else socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                (address, port),
            )
            for address in addresses
        ]

    return resolve


@pytest.mark.parametrize(
    "url",
    [
        "http://shop.example/produto",
        "https://usuario:senha@shop.example/produto",
        "https://shop.example:8443/produto",
        "https://127.0.0.1/produto",
        "https://[::1]/produto",
        "https://shop.example.evil.test/produto",
    ],
)
def test_should_reject_unsafe_url_structures(url):
    with pytest.raises(UnsafeUrlError):
        validate_url_structure(url, allowed_hosts={"shop.example"})


def test_should_accept_exact_allowed_https_host():
    parsed_url = validate_url_structure(
        "https://shop.example/produto?id=1",
        allowed_hosts={"shop.example"},
    )

    assert parsed_url.hostname == "shop.example"


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "10.0.0.10",
        "169.254.169.254",
        "100.64.0.1",
        "0.0.0.0",
        "::1",
        "fe80::1",
    ],
)
def test_should_reject_non_global_dns_results(address):
    with pytest.raises(UnsafeUrlError, match="privada, local ou não roteável"):
        validate_outbound_url(
            "https://shop.example/produto",
            allowed_hosts={"shop.example"},
            resolver=resolver_for(address),
        )


def test_should_reject_mixed_public_and_private_dns_results():
    with pytest.raises(UnsafeUrlError, match="privada, local ou não roteável"):
        validate_outbound_url(
            "https://shop.example/produto",
            allowed_hosts={"shop.example"},
            resolver=resolver_for("93.184.216.34", "10.0.0.10"),
        )


def test_should_accept_exclusively_public_dns_results():
    validate_outbound_url(
        "https://shop.example/produto",
        allowed_hosts={"shop.example"},
        resolver=resolver_for("93.184.216.34", "2606:2800:220:1:248:1893:25c8:1946"),
    )
