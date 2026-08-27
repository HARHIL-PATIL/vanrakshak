"""
VanRakshak AI — Agent 5: Conflict Hotspot Dashboard Agent
==========================================================
Responsibilities:
  - Cluster historical incidents into geographic hotspot zones (simple grid)
  - Identify top 5 hotspot zones by incident density
  - Calculate trend direction (increasing / stable / decreasing)
  - Generate an operational daily summary for Forest Officers

NOTE: IBM Granite LLM is proposed for production to generate richer,
context-aware narrative summaries. This prototype uses template-based
generation.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from data.sample_data import SAMPLE_INCIDENTS, SAMPLE_VILLAGES, SAMPLE_SIGHTINGS

# Grid cell size for simple clustering (degrees)
GRID_SIZE_DEG = 0.15  # ≈ 15–16 km per cell at this latitude


def _grid_cell(lat: float, lon: float) -> tuple[int, int]:
    """Snap lat/lon to a grid cell index."""
    return (int(lat / GRID_SIZE_DEG), int(lon / GRID_SIZE_DEG))


def _cell_centre(cell: tuple[int, int]) -> tuple[float, float]:
    """Return the approximate centre lat/lon of a grid cell."""
    lat = (cell[0] + 0.5) * GRID_SIZE_DEG
    lon = (cell[1] + 0.5) * GRID_SIZE_DEG
    return round(lat, 4), round(lon, 4)


def _days_ago(ts_str, reference: Optional[datetime] = None) -> float:
    """Return fractional days between reference and ts_str."""
    if reference is None:
        reference = datetime.now(timezone.utc)
    try:
        from dateutil.parser import parse as dp
        dt = dp(str(ts_str))
        if dt.tzinfo is None:
            from datetime import timezone as tz
            dt = dt.replace(tzinfo=tz.utc)
        return max((reference - dt).total_seconds() / 86400.0, 0.0)
    except Exception:
        return 9999.0


class HotspotDashboardAgent:
    """
    Agent 5 — Conflict Hotspot Dashboard.

    Analyses historical incident data to identify spatial hotspot zones,
    detect activity trends, and produce officer-facing operational summaries.
    """

    AGENT_NAME = "hotspot_agent"

    def analyze_hotspots(self, top_n: int = 5) -> dict:
        """
        Cluster incidents into geographic grid cells and rank hotspots.

        Algorithm:
            1. Assign each incident to a grid cell based on its village coordinates
            2. Count incidents per cell for 0–15 days (recent) and 15–30 days (older)
            3. Rank cells by total incident count
            4. Compute trend: compare recent vs older count
            5. Attach nearest village name to each hotspot

        Args:
            top_n : Number of top hotspot zones to return (default 5)

        Returns:
            Dict with hotspots, trends, risk_zones, summary, metadata
        """
        now = datetime.now(timezone.utc)

        # ── Build village coordinate lookup ─────────────────────────────
        village_coords: dict[str, tuple[float, float]] = {
            v["village_id"]: (v["lat"], v["lon"])
            for v in SAMPLE_VILLAGES
        }
        village_names: dict[str, str] = {
            v["village_id"]: v["name"]
            for v in SAMPLE_VILLAGES
        }

        # ── Aggregate incidents per grid cell ──────────────────────────
        # cell → {"total": N, "recent": N, "older": N, "types": [...], "villages": set}
        cell_stats: dict[tuple, dict] = defaultdict(lambda: {
            "total": 0, "recent": 0, "older": 0,
            "types": [], "villages": set(), "severities": [],
        })

        for inc in SAMPLE_INCIDENTS:
            vid = inc["village_id"]
            if vid not in village_coords:
                continue
            lat, lon = village_coords[vid]
            cell = _grid_cell(lat, lon)
            days = _days_ago(inc["date"], now)

            cell_stats[cell]["total"]     += 1
            cell_stats[cell]["types"].append(inc["type"])
            cell_stats[cell]["villages"].add(vid)
            cell_stats[cell]["severities"].append(inc["severity"])

            if days <= 15:
                cell_stats[cell]["recent"] += 1
            else:
                cell_stats[cell]["older"]  += 1

        # ── Rank cells ─────────────────────────────────────────────────
        ranked_cells = sorted(
            cell_stats.items(),
            key=lambda kv: (kv[1]["total"], kv[1]["recent"]),
            reverse=True,
        )[:top_n]

        # ── Build hotspot objects ──────────────────────────────────────
        hotspots = []
        for rank, (cell, stats) in enumerate(ranked_cells, start=1):
            clat, clon = _cell_centre(cell)

            # Trend: compare recent (0–15 d) vs older (15–30 d)
            if stats["recent"] > stats["older"] * 1.2:
                trend = "INCREASING"
            elif stats["recent"] < stats["older"] * 0.8:
                trend = "DECREASING"
            else:
                trend = "STABLE"

            # Dominant incident type
            type_counts: dict[str, int] = defaultdict(int)
            for t in stats["types"]:
                type_counts[t] += 1
            dominant_type = max(type_counts, key=type_counts.get) if type_counts else "unknown"

            # Risk level based on count
            if stats["total"] >= 6:
                risk_level = "HIGH"
            elif stats["total"] >= 3:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            # Nearest village names
            vnames = [village_names.get(vid, vid) for vid in stats["villages"]]

            hotspots.append({
                "rank":           rank,
                "zone_id":        f"ZONE-{rank:02d}",
                "centre_lat":     clat,
                "centre_lon":     clon,
                "total_incidents":stats["total"],
                "recent_15d":     stats["recent"],
                "older_15_30d":   stats["older"],
                "trend":          trend,
                "risk_level":     risk_level,
                "dominant_type":  dominant_type,
                "villages":       vnames,
                "is_demo":        True,
            })

        # ── Risk zone summary for map overlay ─────────────────────────
        risk_zones = [
            {
                "zone_id":    h["zone_id"],
                "lat":        h["centre_lat"],
                "lon":        h["centre_lon"],
                "risk_level": h["risk_level"],
                "radius_km":  10,
            }
            for h in hotspots
        ]

        # ── Trend summary across all zones ────────────────────────────
        trend_counts: dict[str, int] = defaultdict(int)
        for h in hotspots:
            trend_counts[h["trend"]] += 1
        overall_trend = max(trend_counts, key=trend_counts.get) if trend_counts else "STABLE"

        # ── Textual summary ───────────────────────────────────────────
        summary = self._build_summary_text(hotspots, overall_trend, now)

        return {
            "agent":         self.AGENT_NAME,
            "hotspots":      hotspots,
            "risk_zones":    risk_zones,
            "overall_trend": overall_trend,
            "summary":       summary,
            "analyzed_at":   now.isoformat(),
            "total_incidents_analyzed": len(SAMPLE_INCIDENTS),
            "llm_note": (
                "PROPOSED INTEGRATION: IBM Granite LLM would generate richer "
                "narrative summaries with ecological context in production. "
                "Template-based summary used in this prototype."
            ),
            "is_demo": True,
        }

    def generate_daily_summary(self) -> str:
        """
        Generate a concise operational daily summary for Forest Officers.

        NOTE: IBM Granite LLM is proposed for production dynamic generation.
        Template-based generation used here as prototype fallback.

        Returns:
            Formatted plain-text summary string
        """
        now      = datetime.now(timezone.utc)
        date_str = now.strftime("%d %b %Y")

        # Quick stats
        incidents_7d   = sum(1 for i in SAMPLE_INCIDENTS if _days_ago(i["date"], now) <= 7)
        incidents_30d  = len(SAMPLE_INCIDENTS)
        high_severity  = sum(1 for i in SAMPLE_INCIDENTS if i["severity"] == "HIGH")
        active         = sum(1 for i in SAMPLE_INCIDENTS if i["status"] in ("NEW", "ASSIGNED", "IN_PROGRESS"))
        sightings_24h  = sum(1 for s in SAMPLE_SIGHTINGS if _days_ago(s["timestamp"], now) <= 1)

        hotspot_data   = self.analyze_hotspots(top_n=3)
        top_zones      = ", ".join(
            f"{h['villages'][0] if h['villages'] else 'Unknown'} ({h['risk_level']})"
            for h in hotspot_data["hotspots"][:3]
        )

        summary = (
            f"═══════════════════════════════════════════════\n"
            f"  VanRakshak AI — Daily Operational Summary\n"
            f"  Date: {date_str} (IST)  |  [DEMO DATA]\n"
            f"═══════════════════════════════════════════════\n"
            f"\n📊 INCIDENT STATISTICS (30-day window)\n"
            f"  • Total recorded incidents : {incidents_30d}\n"
            f"  • Incidents last 7 days    : {incidents_7d}\n"
            f"  • High severity incidents  : {high_severity}\n"
            f"  • Currently active/open    : {active}\n"
            f"\n🦁 WILDLIFE ACTIVITY\n"
            f"  • Sightings last 24 hours  : {sightings_24h}\n"
            f"  • Overall trend            : {hotspot_data['overall_trend']}\n"
            f"\n🗺️  TOP CONFLICT HOTSPOTS\n"
            f"  {top_zones}\n"
            f"\n⚠️  RECOMMENDED ACTIONS\n"
            f"  1. Increase patrol frequency in HIGH-risk zones\n"
            f"  2. Review and action all PENDING officer approvals\n"
            f"  3. Follow up on open compensation claims\n"
            f"  4. Brief village contact persons in HIGH-risk areas\n"
            f"\n───────────────────────────────────────────────\n"
            f"  Generated by VanRakshak AI Agent 5 [PROTOTYPE]\n"
            f"  IBM Granite LLM proposed for production summaries\n"
            f"═══════════════════════════════════════════════\n"
        )
        return summary

    # ── Private helpers ────────────────────────────────────────────────────

    @staticmethod
    def _build_summary_text(hotspots: list, overall_trend: str, now: datetime) -> str:
        """Build a brief hotspot analysis summary paragraph."""
        if not hotspots:
            return "No significant conflict hotspots identified in the current dataset. [DEMO]"

        top = hotspots[0]
        top_villages = ", ".join(top["villages"][:2]) if top["villages"] else "Unknown area"

        return (
            f"Hotspot analysis identified {len(hotspots)} conflict zones in the Gir region. "
            f"The highest-activity zone is near {top_villages} with {top['total_incidents']} "
            f"recorded incidents (trend: {top['trend']}). "
            f"Overall conflict trend across monitored zones is {overall_trend}. "
            f"Dominant conflict type: {top['dominant_type'].replace('_', ' ')}. "
            f"[DEMO — based on synthetic sample data only]"
        )
