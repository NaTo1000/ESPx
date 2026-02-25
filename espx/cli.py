"""ESPx CLI – secure API key management from terminal / PyCharm.

Commands
--------
  espx vault create    – create a new vault
  espx vault store     – store an API key
  espx vault retrieve  – retrieve (print) an API key
  espx vault rotate    – rotate a key
  espx vault delete    – delete a slot
  espx vault list      – list slots
  espx vault audit     – print audit log tail
  espx user add        – add a user
  espx mfa enrol       – enrol a user in MFA
"""

from __future__ import annotations

import getpass
import json
import os
import sys

import click

from espx.vault.vault import (
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    Vault,
)
from espx.vault.access_control import Role
from espx.vault.rotation import RotationPolicy, RotationStrategy
from espx.vault.slots import SlotPolicy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_password(prompt: str = "Vault password") -> str:
    # Respect ESPX_VAULT_PASSWORD env var for non-interactive use
    return os.environ.get("ESPX_VAULT_PASSWORD") or getpass.getpass(f"{prompt}: ")


def _load_vault(vault_path: str) -> Vault:
    password = _get_password()
    try:
        return Vault.load(vault_path, password)
    except AuthenticationError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI groups
# ---------------------------------------------------------------------------


@click.group()
def cli() -> None:
    """ESPx secure API key vault."""


@cli.group()
def vault() -> None:
    """Vault management commands."""


@cli.group()
def user() -> None:
    """User / principal management."""


@cli.group()
def mfa() -> None:
    """Multi-factor authentication management."""


# ---------------------------------------------------------------------------
# vault commands
# ---------------------------------------------------------------------------


@vault.command("create")
@click.argument("vault_path")
@click.option("--owner", required=True, help="Username of the first admin principal")
@click.option("--capacity", default=256, show_default=True, help="Maximum number of slots")
@click.option(
    "--require-mfa",
    is_flag=True,
    default=False,
    help="Require TOTP MFA for every operation",
)
def vault_create(vault_path: str, owner: str, capacity: int, require_mfa: bool) -> None:
    """Create a new vault at VAULT_PATH."""
    password = _get_password("New vault password")
    confirm = _get_password("Confirm password")
    if password != confirm:
        click.echo("Passwords do not match.", err=True)
        sys.exit(1)
    try:
        Vault.create(vault_path, password, owner, capacity=capacity, require_mfa=require_mfa)
        click.echo(f"Vault created at {vault_path} (owner: {owner})")
    except FileExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@vault.command("store")
@click.argument("vault_path")
@click.option("--slot", required=True, help="Slot name")
@click.option("--service", required=True, help="Service (e.g. huggingface, esp-idf)")
@click.option("--actor", required=True, help="Your principal name")
@click.option("--description", default="", help="Optional description")
@click.option("--tags", default="", help="Comma-separated tags")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing slot")
def vault_store(
    vault_path: str,
    slot: str,
    service: str,
    actor: str,
    description: str,
    tags: str,
    overwrite: bool,
) -> None:
    """Store an API key in VAULT_PATH."""
    v = _load_vault(vault_path)
    api_key = getpass.getpass("API key: ")
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    try:
        v.store(
            slot,
            service,
            api_key,
            actor,
            description=description,
            tags=tag_list,
            overwrite=overwrite,
        )
        click.echo(f"Stored key in slot {slot!r} (service: {service})")
    except (AuthorizationError, ValueError, RuntimeError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@vault.command("retrieve")
@click.argument("vault_path")
@click.option("--slot", required=True, help="Slot name")
@click.option("--actor", required=True, help="Your principal name")
@click.option("--mfa-code", default=None, help="TOTP code (if MFA required)")
def vault_retrieve(vault_path: str, slot: str, actor: str, mfa_code: str | None) -> None:
    """Retrieve an API key from VAULT_PATH and print it to stdout."""
    v = _load_vault(vault_path)
    try:
        key = v.retrieve(slot, actor, mfa_code=mfa_code)
        click.echo(key)
    except (AuthorizationError, AuthenticationError, RateLimitError, KeyError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@vault.command("rotate")
@click.argument("vault_path")
@click.option("--slot", required=True, help="Slot name")
@click.option("--actor", required=True, help="Your principal name")
@click.option("--mfa-code", default=None, help="TOTP code (if MFA required)")
def vault_rotate(vault_path: str, slot: str, actor: str, mfa_code: str | None) -> None:
    """Rotate the key for a slot in VAULT_PATH."""
    v = _load_vault(vault_path)
    new_key = getpass.getpass("New API key: ")
    try:
        version = v.rotate(slot, new_key, actor, mfa_code=mfa_code)
        click.echo(f"Key rotated to version {version.version}")
    except (AuthorizationError, AuthenticationError, KeyError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@vault.command("delete")
@click.argument("vault_path")
@click.option("--slot", required=True, help="Slot name")
@click.option("--actor", required=True, help="Your principal name")
@click.option("--mfa-code", default=None, help="TOTP code (if MFA required)")
def vault_delete(vault_path: str, slot: str, actor: str, mfa_code: str | None) -> None:
    """Delete a slot from VAULT_PATH."""
    v = _load_vault(vault_path)
    try:
        v.delete(slot, actor, mfa_code=mfa_code)
        click.echo(f"Slot {slot!r} deleted")
    except (AuthorizationError, AuthenticationError, KeyError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@vault.command("list")
@click.argument("vault_path")
@click.option("--actor", required=True, help="Your principal name")
def vault_list(vault_path: str, actor: str) -> None:
    """List all slots in VAULT_PATH."""
    v = _load_vault(vault_path)
    try:
        slots = v.list_slots(actor)
        if not slots:
            click.echo("No slots found.")
            return
        for s in slots:
            tags = ", ".join(s.get("tags", [])) or "(none)"
            click.echo(
                f"  {s['name']:20s}  service={s['service']:15s}  tags=[{tags}]"
                f"  created={s['created_at']:.0f}"
            )
    except AuthorizationError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@vault.command("audit")
@click.argument("vault_path")
@click.option("--actor", required=True, help="Your principal name (must be admin)")
@click.option("--lines", default=20, show_default=True, help="Number of log lines")
def vault_audit(vault_path: str, actor: str, lines: int) -> None:
    """Print the last N audit log entries for VAULT_PATH."""
    v = _load_vault(vault_path)
    try:
        records = v.audit_tail(actor, n=lines)
        for r in records:
            click.echo(json.dumps(r))
    except AuthorizationError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# user commands
# ---------------------------------------------------------------------------


@user.command("add")
@click.argument("vault_path")
@click.option("--name", required=True, help="New principal name")
@click.option(
    "--role",
    "roles",
    multiple=True,
    type=click.Choice(["admin", "operator", "reader"]),
    default=("reader",),
    help="Role(s) to assign",
)
@click.option("--actor", required=True, help="Your principal name (must be admin)")
def user_add(vault_path: str, name: str, roles: tuple, actor: str) -> None:
    """Add a new user to VAULT_PATH."""
    v = _load_vault(vault_path)
    role_set = {Role(r) for r in roles}
    try:
        v.add_user(name, roles=role_set, actor=actor)
        click.echo(f"User {name!r} added with roles: {roles}")
    except AuthorizationError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# mfa commands
# ---------------------------------------------------------------------------


@mfa.command("enrol")
@click.argument("vault_path")
@click.option("--principal", required=True, help="Principal to enrol")
@click.option("--actor", required=True, help="Your principal name")
def mfa_enrol(vault_path: str, principal: str, actor: str) -> None:
    """Enrol a principal in TOTP MFA for VAULT_PATH."""
    v = _load_vault(vault_path)
    try:
        result = v.enrol_mfa(principal, actor=actor)
        click.echo(f"MFA enrolled for {principal!r}")
        click.echo(f"Secret: {result['secret']}")
        click.echo(f"URI:    {result['uri']}")
        if result.get("qr_ascii"):
            click.echo("\n" + result["qr_ascii"])
    except AuthorizationError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
