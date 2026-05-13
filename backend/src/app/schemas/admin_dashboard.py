from pydantic import BaseModel


class AdminDashboardSummaryResponse(BaseModel):
    device_count: int
    online_device_count: int
    user_count: int
    notification_count: int
    notification_trend: list[dict[str, int | str]]
    device_status_ratio: dict[str, int]
    version_distribution: list[dict[str, int | str]]
