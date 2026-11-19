# Application entry point. Phase 1.
#
# Responsibilities:
#   - Define `main() -> None` and call it under `if __name__ == "__main__":`.
#   - Build the object graph: create the profile repository (pointing at `data/profiles/`),
#     the presenters, and the root `App` window, then start the Tk main loop.
#   - Contain no domain logic and no widget code. If this file grows past ~30 lines, move
#     the extra code into `ui/app.py`.
