from pydantic import BaseModel


class StatusSummary(BaseModel):
    count: int
    total_amount: float


class DealsSummaryResponse(BaseModel):
    by_status: dict[str, StatusSummary]
    avg_won_amount: float
    new_deals_last_n_days: int
    days: int


class StageFunnel(BaseModel):
    total: int
    by_status: dict[str, int]
    conversion_from_prev: float


class DealsFunnelResponse(BaseModel):
    stages: dict[str, StageFunnel]
