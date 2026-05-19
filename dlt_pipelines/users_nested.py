"""Demo pipeline for nested-JSON flattening.

Each user record has a nested address (dict-in-dict) and a nested posts list.
dlt automatically:
  - flattens single nested dicts into prefixed columns on the parent table
  - splits nested lists into child tables with foreign keys (_dlt_parent_id, etc.)

This is the killer feature of dlt for any real REST / event-style source.
"""

from typing import Iterator

import dlt
import requests


@dlt.resource(write_disposition="replace", name="users", primary_key="id")
def users() -> Iterator[dict]:
    """Yield user records with nested address (dict) and nested posts (list)."""
    users_resp = requests.get("https://jsonplaceholder.typicode.com/users", timeout=30)
    users_resp.raise_for_status()
    posts_resp = requests.get("https://jsonplaceholder.typicode.com/posts", timeout=30)
    posts_resp.raise_for_status()

    posts_by_user: dict[int, list[dict]] = {}
    for post in posts_resp.json():
        posts_by_user.setdefault(post["userId"], []).append(
            {"post_id": post["id"], "title": post["title"]}
        )

    for u in users_resp.json():
        yield {
            "id": u["id"],
            "name": u["name"],
            "email": u["email"],
            "address": u["address"],   # nested dict (with another nested dict: geo)
            "company": u["company"],   # nested dict
            "posts": posts_by_user.get(u["id"], []),  # nested list -> child table
        }


@dlt.source(name="users_demo")
def users_demo_source():
    """JSONPlaceholder users with nested address + posts list."""
    return [users()]


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="users_demo_pipeline",
        destination=dlt.destinations.duckdb("data/sandbox.duckdb"),
        dataset_name="raw_users",
    )
    load_info = pipeline.run(users_demo_source())
    print(load_info)
