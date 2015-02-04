from gevent.monkey import patch_all
patch_all()

from chalk_and_cheese_server import add_endpoints
import bottle
import os


def run():
    add_endpoints(bottle)

    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", '0.0.0.0')

    bottle.run(server='gevent',
               host=host, port=port, reloader=True)


if __name__ == "__main__":
    run()