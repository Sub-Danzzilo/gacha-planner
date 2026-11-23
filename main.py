from pathlib import Path

from core.exchange import CurrencyConverter, ManualRateProvider
from services.planner_service import PlannerService
from storage.profile_repository import ProfileRepository
from storage.serializers import ProfileSerializer
from ui.app import App


def main() -> None:
    repository = ProfileRepository(Path("data/profiles"), ProfileSerializer())
    provider = ManualRateProvider()
    service = PlannerService(CurrencyConverter(provider))
    App(repository, provider, service).mainloop()


if __name__ == "__main__":
    main()
