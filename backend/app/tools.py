from .data_loader import (
    load_accounts,
    load_alerts,
    load_assets,
)


def asset_lookup(asset_id: str):
    assets = load_assets()

    for asset in assets:
        if asset["asset_id"] == asset_id:
            return asset

    return None


def user_lookup(account_id: str):
    accounts = load_accounts()

    for account in accounts:
        if account["account_id"] == account_id:
            return account

    return None


def alert_context(alert_id: str):
    alerts = load_alerts()

    for alert in alerts:
        if alert["alert_id"] == alert_id:
            return alert

    return None