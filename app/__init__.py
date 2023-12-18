# file name : __init__.py
# pwd : /jecheon_app/app/__init__.py

from flask import Flask, render_template

import config

def page_not_found(e):
    return render_template('404.html'), 404

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # 블루프린트
    from app.views import main_views, auth_views
    from app.views.adm import dashboard_views, eld_views, app_views, sta_views, mem_views
    from app.views.cmm import notice_views
    from app.views.user_app import user_app_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(dashboard_views.bp)
    app.register_blueprint(eld_views.bp)
    app.register_blueprint(app_views.bp)
    app.register_blueprint(sta_views.bp)
    app.register_blueprint(mem_views.bp)
    app.register_blueprint(notice_views.bp)
    app.register_blueprint(user_app_views.bp)


    from .filter import format_datetime, format_date, format_datetime_ymdhm
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['ymdhm'] = format_datetime_ymdhm


    # markdown
    #Markdown(user_app, extensions=['nl2br', 'fenced_code'])

    # 오류페이지
    app.register_error_handler(404, page_not_found)

    return app


