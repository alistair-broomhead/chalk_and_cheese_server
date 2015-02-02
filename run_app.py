from gevent.monkey import patch_all
patch_all()

from chalk_and_cheese_server import add_endpoints
import bottle
import os


def run():
    app = bottle.Bottle()
    add_endpoints(app)

    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", '0.0.0.0')

    app.run(server='gevent',
            host=host, port=port)


if __name__ == "__main__":
    run()