from app.domain.metrics import METRIC_REGISTRY


def canonicalize_metric(metric_name: str) -> str:
    metric_name = metric_name.lower().strip()

    for canonical, config in METRIC_REGISTRY.items():
        if metric_name == canonical:
            return canonical

        for alias in config["aliases"]:
            if metric_name == alias:
                return canonical

    raise ValueError(f"Unknown metric: {metric_name}")