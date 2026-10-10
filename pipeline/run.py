"""Refresh all PD engine data. From the repo root: pipeline/.venv/Scripts/python pipeline/run.py"""
import describe
import ingest_simplify
import summarize

ingest_simplify.run()
describe.run()
summarize.run()
