"""
SCS Python SDK — bindings for the 25 new SCS services.

Each class takes the top-level SCS client and exposes thin methods over
client.request(). Paths match the server routes under /api/.
"""

from typing import Any, Dict, List, Optional


class _Base:
    def __init__(self, scs):
        self.scs = scs
        self.pid = scs._project_id


# ============================================================================
# Tier 1
# ============================================================================

class SqlService(_Base):
    def list_tables(self):
        return self.scs.request(f"/api/sql/{self.pid}/tables")

    def create_table(self, name: str, columns: List[Dict[str, Any]]):
        return self.scs.request(
            f"/api/sql/{self.pid}/tables",
            method="POST",
            body={"name": name, "columns": columns},
        )

    def describe_table(self, table: str):
        return self.scs.request(f"/api/sql/{self.pid}/tables/{table}")

    def drop_table(self, table: str):
        return self.scs.request(f"/api/sql/{self.pid}/tables/{table}", method="DELETE")

    def insert(self, table: str, row: Dict[str, Any]):
        return self.scs.request(
            f"/api/sql/{self.pid}/tables/{table}/rows",
            method="POST",
            body={"row": row},
        )

    def select(self, table: str, where: Optional[Dict] = None, limit: Optional[int] = None, order_by: Optional[str] = None):
        body = {}
        if where is not None:
            body["where"] = where
        if limit is not None:
            body["limit"] = limit
        if order_by is not None:
            body["orderBy"] = order_by
        return self.scs.request(
            f"/api/sql/{self.pid}/tables/{table}/select",
            method="POST",
            body=body,
        )

    def update(self, table: str, where: Dict, patch: Dict):
        return self.scs.request(
            f"/api/sql/{self.pid}/tables/{table}/rows",
            method="PATCH",
            body={"where": where, "patch": patch},
        )

    def delete(self, table: str, where: Dict):
        return self.scs.request(
            f"/api/sql/{self.pid}/tables/{table}/rows",
            method="DELETE",
            body={"where": where},
        )

    def query(self, sql: str, params: Optional[List] = None):
        return self.scs.request(
            f"/api/sql/{self.pid}/query",
            method="POST",
            body={"sql": sql, "params": params or []},
        )


class MailService(_Base):
    def status(self):
        return self.scs.request("/api/mail/status")

    def send(self, to: str, subject: str, html: Optional[str] = None, text: Optional[str] = None,
             template: Optional[str] = None, variables: Optional[Dict] = None):
        return self.scs.request(
            "/api/mail/send",
            method="POST",
            body={"to": to, "subject": subject, "html": html, "text": text,
                  "template": template, "variables": variables},
        )

    def send_bulk(self, recipients: List[str], subject: str, html: Optional[str] = None, text: Optional[str] = None):
        return self.scs.request(
            "/api/mail/send-bulk",
            method="POST",
            body={"recipients": recipients, "subject": subject, "html": html, "text": text},
        )


class QueueService(_Base):
    def publish(self, topic: str, payload: Any, delay_seconds: int = 0):
        return self.scs.request(
            f"/api/queue/{self.pid}/publish",
            method="POST",
            body={"topic": topic, "payload": payload, "delaySeconds": delay_seconds},
        )

    def pull(self, topic: str, limit: int = 10):
        return self.scs.request(f"/api/queue/pull/{topic}", params={"limit": limit})

    def ack(self, job_id: str):
        return self.scs.request(f"/api/queue/ack/{job_id}", method="POST")

    def nack(self, job_id: str, requeue: bool = True):
        return self.scs.request(f"/api/queue/nack/{job_id}", method="POST", body={"requeue": requeue})

    def stats(self):
        return self.scs.request("/api/queue/stats")


class CronService:
    def __init__(self, scs):
        self.scs = scs

    def list(self):
        return self.scs.request("/api/cron")

    def create(self, name: str, schedule: str, target: Dict, project_id: Optional[str] = None, enabled: bool = True):
        return self.scs.request(
            "/api/cron",
            method="POST",
            body={"name": name, "schedule": schedule, "target": target,
                  "projectId": project_id, "enabled": enabled},
        )

    def set_enabled(self, job_id: str, enabled: bool):
        return self.scs.request(f"/api/cron/{job_id}/enabled", method="PATCH", body={"enabled": enabled})

    def delete(self, job_id: str):
        return self.scs.request(f"/api/cron/{job_id}", method="DELETE")


class VaultService(_Base):
    def list(self):
        return self.scs.request(f"/api/vault/{self.pid}/secrets")

    def set(self, name: str, value: str):
        return self.scs.request(
            f"/api/vault/{self.pid}/secrets",
            method="POST",
            body={"name": name, "value": value},
        )

    def get(self, name: str):
        return self.scs.request(f"/api/vault/{self.pid}/secrets/{name}")

    def delete(self, name: str):
        return self.scs.request(f"/api/vault/{self.pid}/secrets/{name}", method="DELETE")


class AnalyticsService(_Base):
    def track(self, event: str, user_id: Optional[str] = None, session_id: Optional[str] = None,
              properties: Optional[Dict] = None):
        return self.scs.request(
            f"/api/analytics/{self.pid}/track",
            method="POST",
            body={"event": event, "userId": user_id, "sessionId": session_id,
                  "properties": properties or {}},
        )

    def summary(self, range_days: int = 7):
        return self.scs.request(f"/api/analytics/{self.pid}/summary", params={"rangeDays": range_days})

    def query(self, event: Optional[str] = None, user_id: Optional[str] = None, limit: int = 100):
        return self.scs.request(
            f"/api/analytics/{self.pid}/events",
            params={"event": event, "userId": user_id, "limit": limit},
        )


class MonitorService(_Base):
    def list_checks(self, project_id: Optional[str] = None):
        return self.scs.request("/api/monitor/checks", params={"projectId": project_id})

    def create_check(self, name: str, url: str, method: str = "GET",
                     interval_seconds: int = 60, timeout_ms: int = 10000):
        return self.scs.request(
            "/api/monitor/checks",
            method="POST",
            body={"name": name, "url": url, "method": method,
                  "intervalSeconds": interval_seconds, "timeoutMs": timeout_ms,
                  "projectId": self.pid},
        )

    def delete_check(self, check_id: str):
        return self.scs.request(f"/api/monitor/checks/{check_id}", method="DELETE")

    def check_results(self, check_id: str, limit: int = 50):
        return self.scs.request(f"/api/monitor/checks/{check_id}/results", params={"limit": limit})

    def record_metric(self, name: str, value: float, labels: Optional[Dict] = None):
        return self.scs.request(
            f"/api/monitor/{self.pid}/metrics",
            method="POST",
            body={"name": name, "value": value, "labels": labels or {}},
        )

    def query_metric(self, name: str, since_ms: int = 3600000):
        return self.scs.request(f"/api/monitor/{self.pid}/metrics/{name}", params={"sinceMs": since_ms})


# ============================================================================
# Tier 2
# ============================================================================

class SearchService(_Base):
    def upsert(self, index: str, id: Optional[str], fields: Dict):
        return self.scs.request(
            f"/api/search/{self.pid}/{index}/docs",
            method="POST",
            body={"id": id, "fields": fields},
        )

    def delete(self, index: str, doc_id: str):
        return self.scs.request(f"/api/search/{self.pid}/{index}/docs/{doc_id}", method="DELETE")

    def search(self, index: str, q: str, limit: int = 20):
        return self.scs.request(f"/api/search/{self.pid}/{index}/search", params={"q": q, "limit": limit})


class CdnService:
    def __init__(self, scs):
        self.scs = scs

    def fetch(self, url: str, ttl: Optional[int] = None):
        return self.scs.request("/api/cdn/fetch", params={"url": url, "ttl": ttl})

    def purge(self, url: str):
        return self.scs.request("/api/cdn/purge", method="POST", body={"url": url})

    def stats(self):
        return self.scs.request("/api/cdn/stats")


class SmsService:
    def __init__(self, scs):
        self.scs = scs

    def send(self, to: str, message: str, provider: str = "msg91", **kwargs):
        body = {"to": to, "message": message, "provider": provider}
        body.update(kwargs)
        return self.scs.request("/api/sms/send", method="POST", body=body)


class AccessService(_Base):
    def list_roles(self):
        return self.scs.request(f"/api/access/{self.pid}/roles")

    def create_role(self, name: str, permissions: List[str]):
        return self.scs.request(
            f"/api/access/{self.pid}/roles",
            method="POST",
            body={"name": name, "permissions": permissions},
        )

    def delete_role(self, name: str):
        return self.scs.request(f"/api/access/{self.pid}/roles/{name}", method="DELETE")

    def bind(self, user_id: str, role_name: str):
        return self.scs.request(
            f"/api/access/{self.pid}/bindings",
            method="POST",
            body={"userId": user_id, "roleName": role_name},
        )

    def list_bindings(self):
        return self.scs.request(f"/api/access/{self.pid}/bindings")

    def check(self, user_id: str, permission: str):
        return self.scs.request(
            f"/api/access/{self.pid}/check",
            method="POST",
            body={"userId": user_id, "permission": permission},
        )


class PipelineService(_Base):
    def list(self):
        return self.scs.request(f"/api/pipeline/{self.pid}/pipelines")

    def create(self, name: str, steps: List[str], cwd: Optional[str] = None):
        return self.scs.request(
            f"/api/pipeline/{self.pid}/pipelines",
            method="POST",
            body={"name": name, "steps": steps, "cwd": cwd},
        )

    def trigger(self, pipeline_id: str):
        return self.scs.request(f"/api/pipeline/pipelines/{pipeline_id}/trigger", method="POST")

    def get_run(self, run_id: str):
        return self.scs.request(f"/api/pipeline/runs/{run_id}")


class ExperimentsService(_Base):
    def list(self):
        return self.scs.request(f"/api/experiments/{self.pid}")

    def create(self, key: str, variants: List[Dict]):
        return self.scs.request(
            f"/api/experiments/{self.pid}",
            method="POST",
            body={"key": key, "variants": variants},
        )

    def assign(self, key: str, user_id: str):
        return self.scs.request(
            f"/api/experiments/{self.pid}/{key}/assign",
            method="POST",
            body={"userId": user_id},
        )


class InboxService(_Base):
    def send(self, user_id: str, title: str, body: Optional[str] = None, data: Optional[Dict] = None):
        return self.scs.request(
            f"/api/inbox/{self.pid}/send",
            method="POST",
            body={"userId": user_id, "title": title, "body": body, "data": data or {}},
        )

    def list(self, user_id: str, unread: bool = False, limit: int = 50):
        return self.scs.request(
            f"/api/inbox/{self.pid}/users/{user_id}/messages",
            params={"unread": str(unread).lower(), "limit": limit},
        )

    def mark_read(self, message_id: str):
        return self.scs.request(f"/api/inbox/messages/{message_id}/read", method="PATCH")

    def delete(self, message_id: str):
        return self.scs.request(f"/api/inbox/messages/{message_id}", method="DELETE")


class LinksService(_Base):
    def create(self, web: str, slug: Optional[str] = None, android: Optional[str] = None,
               ios: Optional[str] = None, meta: Optional[Dict] = None):
        return self.scs.request(
            f"/api/links/{self.pid}",
            method="POST",
            body={"web": web, "slug": slug, "android": android, "ios": ios, "meta": meta or {}},
        )

    def list(self):
        return self.scs.request(f"/api/links/{self.pid}")

    def delete(self, slug: str):
        return self.scs.request(f"/api/links/{slug}", method="DELETE")


# ============================================================================
# Tier 3 — observability
# ============================================================================

class CrashService(_Base):
    def report(self, name: str, message: Optional[str] = None, stack: Optional[str] = None,
               user_id: Optional[str] = None, context: Optional[Dict] = None, platform: Optional[str] = None):
        return self.scs.request(
            f"/api/crash/{self.pid}/report",
            method="POST",
            body={"name": name, "message": message, "stack": stack,
                  "userId": user_id, "context": context or {}, "platform": platform},
        )

    def groups(self, limit: int = 50):
        return self.scs.request(f"/api/crash/{self.pid}/groups", params={"limit": limit})

    def events(self, group_id: str, limit: int = 50):
        return self.scs.request(f"/api/crash/groups/{group_id}/events", params={"limit": limit})


class PerfService(_Base):
    def record(self, name: str, duration_ms: float, attributes: Optional[Dict] = None):
        return self.scs.request(
            f"/api/perf/{self.pid}/traces",
            method="POST",
            body={"name": name, "durationMs": duration_ms, "attributes": attributes or {}},
        )

    def summary(self, range_days: int = 1):
        return self.scs.request(f"/api/perf/{self.pid}/summary", params={"rangeDays": range_days})


# ============================================================================
# Extra GCP
# ============================================================================

class DnsService(_Base):
    def list_zones(self):
        return self.scs.request(f"/api/dns/{self.pid}/zones")

    def create_zone(self, domain: str):
        return self.scs.request(f"/api/dns/{self.pid}/zones", method="POST", body={"domain": domain})

    def list_records(self, zone_id: str):
        return self.scs.request(f"/api/dns/zones/{zone_id}/records")

    def add_record(self, zone_id: str, name: str, type: str, value: str, ttl: int = 300):
        return self.scs.request(
            f"/api/dns/zones/{zone_id}/records",
            method="POST",
            body={"name": name, "type": type, "value": value, "ttl": ttl},
        )

    def delete_record(self, record_id: str):
        return self.scs.request(f"/api/dns/records/{record_id}", method="DELETE")

    def export_zone(self, zone_id: str):
        return self.scs.request(f"/api/dns/zones/{zone_id}/export")


class TranslateService:
    def __init__(self, scs):
        self.scs = scs

    def translate(self, text: str, target: str, source: Optional[str] = None,
                  provider_config: Optional[Dict] = None):
        return self.scs.request(
            "/api/translate",
            method="POST",
            body={"text": text, "target": target, "source": source,
                  "providerConfig": provider_config or {}},
        )


class WarehouseService(_Base):
    def datasets(self):
        return self.scs.request(f"/api/warehouse/{self.pid}/datasets")

    def query(self, dataset: str, sql: str, params: Optional[List] = None):
        return self.scs.request(
            f"/api/warehouse/{self.pid}/{dataset}/query",
            method="POST",
            body={"sql": sql, "params": params or []},
        )


class ArtifactService(_Base):
    def list(self):
        return self.scs.request(f"/api/artifact/{self.pid}")

    def upload(self, name: str, version: str, data: str, content_type: str = "application/octet-stream"):
        return self.scs.request(
            f"/api/artifact/{self.pid}/upload",
            method="POST",
            body={"name": name, "version": version, "data": data, "contentType": content_type},
        )

    def download(self, name: str, version: str):
        return self.scs.request(f"/api/artifact/{self.pid}/{name}/{version}")


class BillingService(_Base):
    def record(self, metric: str, qty: float = 1, meta: Optional[Dict] = None):
        return self.scs.request(
            f"/api/billing/{self.pid}/usage",
            method="POST",
            body={"metric": metric, "qty": qty, "meta": meta or {}},
        )

    def summary(self, since_ms: int = 30 * 24 * 3600 * 1000):
        return self.scs.request(f"/api/billing/{self.pid}/summary", params={"sinceMs": since_ms})


class WorkflowsService(_Base):
    def list(self):
        return self.scs.request(f"/api/workflows/{self.pid}")

    def create(self, name: str, steps: List[Dict]):
        return self.scs.request(
            f"/api/workflows/{self.pid}",
            method="POST",
            body={"name": name, "steps": steps},
        )

    def execute(self, workflow_id: str, input: Optional[Dict] = None):
        return self.scs.request(
            f"/api/workflows/workflows/{workflow_id}/execute",
            method="POST",
            body={"input": input or {}},
        )

    def get_execution(self, exec_id: str):
        return self.scs.request(f"/api/workflows/executions/{exec_id}")


class IotService(_Base):
    def register_device(self, device_id: str, meta: Optional[Dict] = None):
        return self.scs.request(
            f"/api/iot/{self.pid}/devices",
            method="POST",
            body={"deviceId": device_id, "meta": meta or {}},
        )

    def list_devices(self):
        return self.scs.request(f"/api/iot/{self.pid}/devices")

    def ingest(self, device_id: str, token: str, payload: Any):
        return self.scs.request(
            "/api/iot/ingest",
            method="POST",
            body={"deviceId": device_id, "token": token, "payload": payload},
        )

    def telemetry(self, device_id: str, limit: int = 50):
        return self.scs.request(f"/api/iot/devices/{device_id}/telemetry", params={"limit": limit})


class FirewallService:
    def __init__(self, scs):
        self.scs = scs

    def list_rules(self):
        return self.scs.request("/api/firewall/rules")

    def add_rule(self, match: Dict, action: str = "deny"):
        return self.scs.request(
            "/api/firewall/rules",
            method="POST",
            body={"action": action, "match": match},
        )

    def delete_rule(self, rule_id: str):
        return self.scs.request(f"/api/firewall/rules/{rule_id}", method="DELETE")
