"""Gunicorn import target for the M2-M0 Cloud Run deployment."""

from .cloud_run import build_cloud_run_wsgi_app


app = build_cloud_run_wsgi_app()
