"""Run the Lookout once. Prints review items; never changes a rule pack."""
import json

from ..lookout import drift
from ..lookout.tavily import Tavily
from ..watch.state import State


def main(argv=None):
    st = State("dogwatch-state.db")
    rep = drift.run(Tavily(), st)
    print(json.dumps({"status": rep.status, "items": rep.items, "detail": rep.detail}, indent=2))


if __name__ == "__main__":
    main()
