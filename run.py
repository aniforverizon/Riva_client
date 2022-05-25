import flask_app
from flask_app import factory

if __name__ == "run":
    app = factory.create_app(celery=flask_app.celery)
    # app.run(host = '0.0.0.0', port = 8081, debug=True, threaded = True)
    # app.run()
