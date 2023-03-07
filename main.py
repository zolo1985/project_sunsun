import os
from datetime import timedelta

from flask import session

from webapp import create_app
from webapp.cli import register
from webapp.database import Connection

env = os.environ.get('WEBAPP_ENV')
app = create_app('config.%sConfig' % env.capitalize())
register(app)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)

@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers["Cache-Control"] = "must-revalidate=86400, max-age=60"
    response.headers["Strict-Transport-Security"] = "max-age=31536000 ; includeSubDomains"
    response.headers["X-Frame-Options"] = "deny"
    return response

@app.teardown_appcontext
def shutdown_session(exception):
    print("******************************** CONNNECTION REMOVED ************************************************")
    if exception:
        connection = Connection()
        connection.rollback()
    Connection.remove()

@app.teardown_request
def teardown_request(exception):
    print("******************************** CONNNECTION REMOVED ************************************************")
    if exception:
        connection = Connection()
        connection.rollback()
    Connection.remove()

@app.context_processor
def diffdates():
    def _diffdates(d1, d2):
        timeDiff = d1.replace(tzinfo=None) - d2.replace(tzinfo=None)
        return timeDiff.total_seconds() / 60
    return dict(diffdates=_diffdates)

if __name__ == '__main__':
    app.run(host='0.0.0.0')