#!/usr/bin/env bash
set -Eeuo pipefail

# Universal Menu bootstrap installer.
# Installs the compatible Hermes branch in a separate checkout, then installs
# the plugin into the selected profile. No secrets are read or written.

PLUGIN_REPO="${UNIVERSAL_MENU_REPO:-https://github.com/Staxan/hermes-universal-menu.git}"
HERMES_REPO="${UNIVERSAL_MENU_HERMES_REPO:-https://github.com/Staxan/hermes-agent.git}"
HERMES_REF="${UNIVERSAL_MENU_HERMES_REF:-feat/universal-menu-telegram}"
HERMES_EXPECTED_SHA="${UNIVERSAL_MENU_HERMES_SHA:-7c4cde9e824771ea64856b92acfde65e4de986c9}"
PROFILE="${HERMES_PROFILE:-${1:-nika-redaktor}}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
CHECKOUT="$HERMES_HOME/hermes-agent-universal-menu"
BACKUP_ROOT="$HERMES_HOME/backups/universal-menu"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$BACKUP_ROOT/$STAMP"

say() { printf '[universal-menu] %s\n' "$*"; }
fatal() { printf '[universal-menu] ERROR: %s\n' "$*" >&2; exit 1; }

command -v git >/dev/null || fatal "git is required"
command -v hermes >/dev/null || fatal "hermes CLI is required"

if [[ "$PROFILE" == -* || "$PROFILE" == */* || "$PROFILE" == *..* ]]; then
  fatal "invalid profile name: $PROFILE"
fi

mkdir -p "$BACKUP_ROOT"

# Keep the currently used installation recoverable. Never copy secrets into a
# Git checkout; backup is local and owner-only.
if [[ -d "$HOME/.hermes/profiles/$PROFILE" ]]; then
  mkdir -p "$BACKUP"
  cp -a "$HOME/.hermes/profiles/$PROFILE" "$BACKUP/profile"
  chmod -R u=rwX,go= "$BACKUP"
  say "profile backup: $BACKUP/profile"
fi

if [[ -e "$CHECKOUT/.git" ]]; then
  git -C "$CHECKOUT" fetch --depth 1 origin "$HERMES_REF"
  git -C "$CHECKOUT" checkout -B "$HERMES_REF" "FETCH_HEAD"
else
  rm -rf "$CHECKOUT.tmp"
  git clone --depth 1 --branch "$HERMES_REF" "$HERMES_REPO" "$CHECKOUT.tmp"
  mv "$CHECKOUT.tmp" "$CHECKOUT"
fi

# Compatibility gate: this branch must expose the stable handler extension API.
grep -q 'def register_telegram_handler' "$CHECKOUT/hermes_cli/plugins.py" \
  || fatal "Hermes branch lacks register_telegram_handler"
grep -q 'def _wire_plugin_handlers' "$CHECKOUT/plugins/platforms/telegram/adapter.py" \
  || fatal "Hermes branch lacks Telegram plugin wiring"

ACTUAL_SHA="$(git -C "$CHECKOUT" rev-parse HEAD)"
if [[ -n "$HERMES_EXPECTED_SHA" && "$ACTUAL_SHA" != "$HERMES_EXPECTED_SHA" ]]; then
  fatal "unexpected Hermes revision: $ACTUAL_SHA (expected $HERMES_EXPECTED_SHA)"
fi
say "compatible Hermes checkout: $ACTUAL_SHA"

# Keep the working Hermes virtualenv/CLI (and its dependencies), but put the
# compatible checkout first on PYTHONPATH. The global installation is not
# overwritten.
hermes_cli() {
  PYTHONPATH="$CHECKOUT${PYTHONPATH:+:$PYTHONPATH}" \
    hermes "$@"
}

hermes_cli --profile "$PROFILE" plugins install "$PLUGIN_REPO" --force --enable

# Verify discovery before asking the user to restart a gateway.
if ! hermes_cli --profile "$PROFILE" plugins list --plain --no-bundled \
    | grep -Eq '(^|[[:space:]])universal-menu([[:space:]]|$)'; then
  fatal "Universal Menu was not discovered after installation"
fi


say "installed Universal Menu in profile: $PROFILE"
say "restart only this profile's Gateway to activate Telegram handlers:"
say "  hermes --profile $PROFILE gateway run"
say "rollback profile files if needed:"
say "  rm -rf \"$HOME/.hermes/profiles/$PROFILE\" && cp -a \"$BACKUP/profile\" \"$HOME/.hermes/profiles/$PROFILE\""
