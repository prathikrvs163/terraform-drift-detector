import html
from datetime import datetime, timezone
from pathlib import Path


class ReportGenerator:

    # action -> (badge css class, icon)
    ACTIONS = {
        "create":  ("create",  "🟢"),
        "update":  ("update",  "🟠"),
        "delete":  ("delete",  "🔴"),
        "replace": ("replace", "🟣"),
    }

    # nicer display names for common resource types
    TYPE_NAMES = {
        "azurerm_storage_account":           "Storage Account",
        "azurerm_resource_group":            "Resource Group",
        "azurerm_virtual_network":           "Virtual Network",
        "azurerm_subnet":                    "Subnet",
        "azurerm_network_security_group":    "Network Security Group",
        "azurerm_linux_virtual_machine":     "Linux Virtual Machine",
        "azurerm_windows_virtual_machine":   "Windows Virtual Machine",
        "azurerm_virtual_machine":           "Virtual Machine",
        "azurerm_kubernetes_cluster":        "Kubernetes Cluster",
        "azurerm_key_vault":                 "Key Vault",
        "azurerm_app_service":               "App Service",
        "azurerm_public_ip":                 "Public IP",
    }

    # provider prefixes to strip in the fallback prettifier
    PROVIDER_PREFIXES = (
        "azurerm_", "azuread_", "aws_", "google_", "kubernetes_",
        "helm_", "random_", "tls_", "null_", "local_", "archive_",
    )

    # words that should stay uppercased
    ACRONYMS = {
        "id": "ID", "ip": "IP", "vm": "VM", "db": "DB", "dns": "DNS",
        "vpc": "VPC", "sql": "SQL", "ssl": "SSL", "cdn": "CDN",
        "api": "API", "vnet": "VNet", "nsg": "NSG", "lb": "LB",
        "os": "OS", "aks": "AKS", "acr": "ACR", "kv": "KV",
    }

    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent
        self.template_file = self.project_root / "templates" / "report.html"
        self.report_dir = self.project_root / "reports"
        self.report_dir.mkdir(exist_ok=True)

    def generate_html(self, resources, checked=None):
        """
        resources : list of drifted resources, each:
            {
                "resource": "azurerm_storage_account.storage",
                "action": "update",
                "changes": [
                    {"property": "...", "azure": "...", "terraform": "..."},
                    ...
                ],
            }
        checked   : total number of resources scanned. Pass
                    len(plan["resource_changes"]) from detector.py.
                    Defaults to the drifted count if not supplied.
        """
        now = datetime.now(timezone.utc)
        gen_date = now.strftime("%d %b %Y")
        gen_time = now.strftime("%H:%M UTC")

        drifted = len(resources)
        checked = checked if checked is not None else drifted
        in_sync = max(checked - drifted, 0)

        if drifted:
            status, status_class, drift_card_class = "⚠ Drift Detected", "drift", "has-drift"
        else:
            status, status_class, drift_card_class = "✅ No Drift", "ok", ""

        panels = self._build_panels(resources)

        html_out = (
            self.template_file.read_text(encoding="utf-8")
            .replace("{{generated_date}}", html.escape(gen_date))
            .replace("{{generated_time}}", html.escape(gen_time))
            .replace("{{status}}", status)
            .replace("{{status_class}}", status_class)
            .replace("{{checked}}", str(checked))
            .replace("{{drifted}}", str(drifted))
            .replace("{{in_sync}}", str(in_sync))
            .replace("{{drift_card_class}}", drift_card_class)
            .replace("{{resource_panels}}", panels)
        )

        output = self.report_dir / "drift_report.html"
        output.write_text(html_out, encoding="utf-8")
        return output

    def _pretty_type(self, resource_type):
        """azurerm_storage_account -> 'Storage Account'."""
        if resource_type in self.TYPE_NAMES:
            return self.TYPE_NAMES[resource_type]

        name = resource_type
        for prefix in self.PROVIDER_PREFIXES:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break

        words = [self.ACRONYMS.get(w, w.capitalize()) for w in name.split("_")]
        return " ".join(words) or resource_type

    def _build_panels(self, resources):
        if not resources:
            return (
                '<div class="empty">'
                '<div class="mark">✅</div>'
                "<h2>Everything is in sync</h2>"
                "<p>No drift detected between your Terraform state and live infrastructure.</p>"
                "</div>"
            )

        panels = []
        for resource in resources:
            action = str(resource.get("action", "")).lower()
            badge_class, icon = self.ACTIONS.get(action, ("update", "🟠"))

            full_id = str(resource.get("resource", "unknown"))
            res_type = full_id.split(".")[0]
            pretty = html.escape(self._pretty_type(res_type))
            name = html.escape(full_id)

            rows = []
            for change in resource.get("changes", []):
                prop = html.escape(str(change.get("property", "")))
                actual = html.escape(str(change.get("azure", "")))
                expected = html.escape(str(change.get("terraform", "")))
                rows.append(
                    "<tr>"
                    f'<td class="prop">{prop}</td>'
                    f'<td><span class="val expected">{expected}</span></td>'
                    f'<td><span class="val actual">{actual}</span></td>'
                    "</tr>"
                )

            badge_label = f"{icon} {html.escape(action).upper()}" if action else f"{icon} CHANGE"

            panels.append(
                '<div class="resource">'
                '<div class="resource-head">'
                '<div class="resource-meta">'
                f'<span class="resource-type">{pretty}</span>'
                f'<span class="resource-name">{name}</span>'
                "</div>"
                f'<span class="badge {badge_class}">{badge_label}</span>'
                "</div>"
                "<table>"
                "<thead><tr>"
                "<th>Property</th><th>Expected (Terraform)</th><th>Actual (Azure)</th>"
                "</tr></thead>"
                f"<tbody>{''.join(rows)}</tbody>"
                "</table>"
                "</div>"
            )

        return "\n".join(panels)