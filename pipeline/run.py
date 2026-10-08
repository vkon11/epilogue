"""Refresh all PD engine data. From the repo root: pipeline/.venv/Scripts/python pipeline/run.py"""
import describe
import eligibility
import ingest_simplify

ingest_simplify.run()
describe.run()
eligibility.run()
