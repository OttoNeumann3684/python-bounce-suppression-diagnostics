import json
import sys

from bounce_service import handle_bounce
from infrai_client import InfraiClient


def main() -> None:
    event = json.load(sys.stdin)
    result = handle_bounce(event, InfraiClient())
    print(json.dumps({"address": result.address, "action": result.action, "message": result.message}))


if __name__ == "__main__":
    main()

