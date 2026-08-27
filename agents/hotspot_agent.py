# ============================================================
# VanRakshak AI — Agent 5: Conflict Hotspot Dashboard Agent
# Clusters incidents by location, calculates hotspot intensity,
# identifies trending areas, generates text summaries.
# ============================================================

import math
from datetime import datetime, timedelta
from collections import defaultdict


class HotspotAgent:
    """
    Agent 5 — Conflict Hotspot Dashboard Agent.
    Uses distance-based clustering (no external libs required) to identify
    geographic conflict hotspots and compute intensity scores.
    """

    NAME = "HotspotAgent"
    VERSION = "1.0-PROTOTYPE"
    CLUSTER_RADIUS_KM = 15.0   # incidents within 15 km are in the same cluster

    def __init__(self):
        self.status = "IDLE"
        self.last_action = None
        self.last_confidence = None
        self.last_run = None
        self.total_processed = 0

    # ------------------------------------------------------------------

    def process(self, incidents: list, sightings: list, villages: list) -> dict:
        """
        Analyse incidents + sightings to produce hotspot clusters.

        Returns
        -------
        {
            hotspots: list[hotspot],
            trending_areas: list,
            risk_rankings: list,
            weekly_summary: str,
            daily_summary: str,
            confidence: float,
            agent_meta: dict,
        }
        """
        self.status = "PROCESSING"

        clusters   = self._cluster_incidents(incidents, villages)
        hotspots   = self._score_hotspots(clusters, incidents, sightings, villages)
        trending   = self._identify_trending(incidents, villages)
        rankings   = self._village_risk_rankings(hotspots, villages)
        daily_sum  = self._daily_summary(incidents, sightings)
        weekly_sum = self._weekly_summary(incidents, hotspots)

        confidence = min(0.92, 0.65 + 0.03 * min(len(incidents), 9))

        result = {
            "hotspots":      hotspots,
            "trending_areas": trending,
            "risk_rankings": rankings,
            "daily_summary": daily_sum,
            "weekly_summary": weekly_sum,
            "confidence":    round(confidence, 2),
            "agent_meta": {
                "agent":      self.NAME,
                "version":    self.VERSION,
                "timestamp":  datetime.utcnow().isoformat(),
                "disclaimer": "PROTOTYPE — hotspot analysis is indicative only",
            },
        }

        self.status = "IDLE"
        self.last_action = f"{len(hotspots)} hotspot clusters identified"
        self.last_confidence = round(confidence, 2)
        self.last_run = datetime.utcnow().isoformat()
        self.total_processed += 1

        return result

    # ------------------------------------------------------------------
    # Clustering
    # ------------------------------------------------------------------

    def _cluster_incidents(self, incidents: list, villages: list) -> list:
        """
        Simple greedy distance-based clustering.
        Returns list of clusters: [{"center_village": ..., "incident_ids": [...]}]
        """
        village_map = {v["id"]: v for v in villages}
        clusters = []

        for inc in incidents:
            vid = inc.get("village_id")
            v   = village_map.get(vid)
            if not v:
                continue

            lat, lon = v["lat"], v["lon"]
            placed = False
            for cluster in clusters:
                cv = village_map.get(cluster["center_village_id"])
                if not cv:
                    continue
                if _haversine(lat, lon, cv["lat"], cv["lon"]) <= self.CLUSTER_RADIUS_KM:
                    cluster["incident_ids"].append(inc["id"])
                    cluster["village_ids"].add(vid)
                    placed = True
                    break

            if not placed:
                clusters.append({
                    "center_village_id": vid,
                    "center_village_name": v["name"],
                    "incident_ids": [inc["id"]],
                    "village_ids": {vid},
                    "lat": lat,
                    "lon": lon,
                })

        return clusters

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _score_hotspots(self, clusters: list, incidents: list,
                        sightings: list, villages: list) -> list:
        """Compute intensity score for each cluster."""
        inc_map  = {i["id"]: i for i in incidents}
        village_map = {v["id"]: v for v in villages}
        now = datetime.utcnow()
        hotspots = []

        for cluster in clusters:
            inc_list = [inc_map[iid] for iid in cluster["incident_ids"] if iid in inc_map]

            # Base intensity: number of incidents (normalised)
            base = min(1.0, len(inc_list) / 6.0)

            # Recency boost: incidents in last 7 days count double
            recency_score = 0.0
            for inc in inc_list:
                try:
                    ts = datetime.fromisoformat(inc["timestamp"])
                    days_ago = (now - ts).days
                    recency_score += max(0, (7 - days_ago) / 7.0)
                except (ValueError, KeyError):
                    pass
            recency_norm = min(1.0, recency_score / max(1, len(inc_list)))

            # Species severity
            species_scores = []
            for inc in inc_list:
                s = inc.get("species", "")
                if s == "Asiatic Lion":
                    species_scores.append(1.0)
                elif s == "Leopard":
                    species_scores.append(0.85)
                elif s == "Hyena":
                    species_scores.append(0.55)
                else:
                    species_scores.append(0.30)
            species_avg = sum(species_scores) / max(1, len(species_scores))

            # Nearby sightings in last 48 h
            nearby_sig = sum(
                1 for s in sightings
                if s.get("nearest_village") in cluster["village_ids"]
                and self._is_recent(s.get("timestamp", ""), 48)
            )
            sighting_factor = min(1.0, nearby_sig / 5.0)

            intensity = (
                0.35 * base +
                0.30 * recency_norm +
                0.20 * species_avg +
                0.15 * sighting_factor
            )
            intensity = round(min(1.0, intensity), 3)

            if intensity >= 0.70:
                level = "CRITICAL"
            elif intensity >= 0.45:
                level = "HIGH"
            elif intensity >= 0.25:
                level = "MODERATE"
            else:
                level = "LOW"

            hotspots.append({
                "hotspot_id":     f"HS-{len(hotspots)+1:03d}",
                "center_village": cluster["center_village_name"],
                "center_lat":     cluster["lat"],
                "center_lon":     cluster["lon"],
                "incident_count": len(inc_list),
                "village_ids":    list(cluster["village_ids"]),
                "intensity":      intensity,
                "level":          level,
                "recent_24h":     sum(1 for i in inc_list if self._is_recent(i.get("timestamp",""), 24)),
                "recent_7d":      sum(1 for i in inc_list if self._is_recent(i.get("timestamp",""), 168)),
                "dominant_species": self._dominant_species(inc_list),
            })

        hotspots.sort(key=lambda h: h["intensity"], reverse=True)
        return hotspots

    # ------------------------------------------------------------------
    # Trend detection
    # ------------------------------------------------------------------

    def _identify_trending(self, incidents: list, villages: list) -> list:
        """Villages with increasing incident rate over the last 7 days vs previous 7."""
        village_map = {v["id"]: v for v in villages}
        now = datetime.utcnow()
        counts_recent = defaultdict(int)
        counts_prior  = defaultdict(int)

        for inc in incidents:
            vid = inc.get("village_id")
            try:
                ts = datetime.fromisoformat(inc["timestamp"])
            except (ValueError, KeyError):
                continue
            days = (now - ts).days
            if days <= 7:
                counts_recent[vid] += 1
            elif days <= 14:
                counts_prior[vid] += 1

        trending = []
        for vid, recent in counts_recent.items():
            prior = counts_prior.get(vid, 0)
            if recent > prior or (recent >= 2 and prior == 0):
                v = village_map.get(vid, {})
                trending.append({
                    "village_id":   vid,
                    "village_name": v.get("name", vid),
                    "recent_7d":    recent,
                    "prior_7d":     prior,
                    "trend":        "INCREASING" if recent > prior else "EMERGING",
                })

        trending.sort(key=lambda t: t["recent_7d"], reverse=True)
        return trending

    # ------------------------------------------------------------------
    # Rankings
    # ------------------------------------------------------------------

    def _village_risk_rankings(self, hotspots: list, villages: list) -> list:
        """
        Rank all villages by hotspot intensity; villages not in any hotspot get score 0.
        """
        village_map = {v["id"]: v for v in villages}
        ranked = {}

        for hs in hotspots:
            for vid in hs["village_ids"]:
                if hs["intensity"] > ranked.get(vid, {}).get("intensity", -1):
                    ranked[vid] = {
                        "village_id":   vid,
                        "village_name": village_map.get(vid, {}).get("name", vid),
                        "intensity":    hs["intensity"],
                        "level":        hs["level"],
                        "hotspot_id":   hs["hotspot_id"],
                    }

        for v in villages:
            if v["id"] not in ranked:
                ranked[v["id"]] = {
                    "village_id":   v["id"],
                    "village_name": v["name"],
                    "intensity":    0.0,
                    "level":        "NONE",
                    "hotspot_id":   None,
                }

        return sorted(ranked.values(), key=lambda x: x["intensity"], reverse=True)

    # ------------------------------------------------------------------
    # Summaries
    # ------------------------------------------------------------------

    def _daily_summary(self, incidents: list, sightings: list) -> str:
        today_incs  = sum(1 for i in incidents if self._is_recent(i.get("timestamp",""), 24))
        today_sight = sum(1 for s in sightings if self._is_recent(s.get("timestamp",""), 24))
        high_today  = sum(1 for i in incidents
                          if self._is_recent(i.get("timestamp",""), 24)
                          and i.get("severity") == "HIGH")
        return (
            f"[SAMPLE DATA] Last 24 hours: {today_sight} wildlife sighting(s) recorded, "
            f"{today_incs} incident(s) logged ({high_today} HIGH severity). "
            f"Forest Department alerted. Monitoring continues."
        )

    def _weekly_summary(self, incidents: list, hotspots: list) -> str:
        week_incs = sum(1 for i in incidents if self._is_recent(i.get("timestamp",""), 168))
        critical  = sum(1 for h in hotspots if h["level"] == "CRITICAL")
        high      = sum(1 for h in hotspots if h["level"] == "HIGH")
        return (
            f"[SAMPLE DATA] Last 7 days: {week_incs} conflict incidents. "
            f"{critical} CRITICAL and {high} HIGH hotspot zones identified. "
            f"Highest-risk areas: "
            + ", ".join(h["center_village"] for h in hotspots[:3])
            + ". Recommend increased patrol frequency in these zones."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_recent(timestamp_str: str, hours: int) -> bool:
        try:
            ts = datetime.fromisoformat(timestamp_str)
            return (datetime.utcnow() - ts).total_seconds() / 3600 <= hours
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _dominant_species(inc_list: list) -> str:
        counts = defaultdict(int)
        for inc in inc_list:
            counts[inc.get("species", "Unknown")] += 1
        if not counts:
            return "Unknown"
        return max(counts, key=counts.get)

    def get_status(self) -> dict:
        return {
            "agent":            self.NAME,
            "status":           self.status,
            "last_action":      self.last_action,
            "last_confidence":  self.last_confidence,
            "last_run":         self.last_run,
            "total_processed":  self.total_processed,
            "escalation_state": "NONE",
        }


def _haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))
