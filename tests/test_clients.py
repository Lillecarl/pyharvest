from __future__ import annotations

import datetime as dt
import json
from typing import TYPE_CHECKING

import pytest

from pyharvest.models.clients import (
    ClientCreate,
    ClientUpdate,
    Contact,
    ContactCreate,
    ContactUpdate,
    InvoiceRecipientStatus,
)
from pyharvest.resources.clients import Clients, Contacts

from . import fixtures, fixtures_clients

if TYPE_CHECKING:
    import respx

    from pyharvest import Harvest


@pytest.mark.anyio
async def test_list_clients_renders_filters(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.get("clients").respond(
        json=fixtures.page("clients", [fixtures_clients.client()], None)
    )

    clients = [
        c
        async for c in Clients(harvest._session).list(
            is_active=True,
            updated_since=dt.datetime(2024, 3, 1, 12, tzinfo=dt.UTC),
        )
    ]

    assert clients[0].name == "ABC Corp"
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "is_active": "true",
        "updated_since": "2024-03-01T12:00:00Z",
    }


@pytest.mark.anyio
async def test_create_client_sends_only_set_fields(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.post("clients").respond(201, json=fixtures_clients.client())

    await Clients(harvest._session).create(ClientCreate(name="ABC Corp"))

    assert json.loads(route.calls.last.request.content) == {"name": "ABC Corp"}


@pytest.mark.anyio
async def test_update_client_clears_address(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.patch("clients/2").respond(
        json=fixtures_clients.client(address=None)
    )

    client = await Clients(harvest._session).update(2, ClientUpdate(address=None))

    assert client.address is None
    assert json.loads(route.calls.last.request.content) == {"address": None}


@pytest.mark.anyio
async def test_delete_client(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.delete("clients/2").respond(200)

    await Clients(harvest._session).delete(2)

    assert route.called


@pytest.mark.anyio
async def test_list_contacts_renders_filters(
    harvest: Harvest, router: respx.MockRouter
) -> None:
    route = router.get("contacts").respond(
        json=fixtures.page("contacts", [fixtures_clients.contact()], None)
    )

    contacts = [c async for c in Contacts(harvest._session).list(client_id=2)]

    assert contacts[0].client.id == 2
    assert contacts[0].invoice_recipient_status is InvoiceRecipientStatus.NONE
    assert dict(route.calls.last.request.url.params) == {
        "per_page": "2000",
        "client_id": "2",
    }


@pytest.mark.anyio
async def test_create_contact_body(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.post("contacts").respond(201, json=fixtures_clients.contact())

    await Contacts(harvest._session).create(
        ContactCreate(
            client_id=2,
            first_name="Jane",
            email="jane@example.com",
            invoice_recipient_status=InvoiceRecipientStatus.CC,
        )
    )

    assert json.loads(route.calls.last.request.content) == {
        "client_id": 2,
        "first_name": "Jane",
        "email": "jane@example.com",
        "invoice_recipient_status": "cc",
    }


@pytest.mark.anyio
async def test_update_contact_body(harvest: Harvest, router: respx.MockRouter) -> None:
    route = router.patch("contacts/7").respond(json=fixtures_clients.contact())

    await Contacts(harvest._session).update(7, ContactUpdate(title=None, fax="1"))

    assert json.loads(route.calls.last.request.content) == {"title": None, "fax": "1"}


def test_contact_without_recipient_status_parses() -> None:
    raw = fixtures_clients.contact()
    del raw["invoice_recipient_status"]

    assert Contact.model_validate(raw).invoice_recipient_status is None
    unknown = Contact.model_validate(
        fixtures_clients.contact(invoice_recipient_status="to")
    )
    assert unknown.invoice_recipient_status == "to"
