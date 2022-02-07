from datetime import datetime
from dotenv import load_dotenv
from github import Github
import json
import os
from pprint import pprint

# Is "True" when file is executed directly
# Is "False" if file is imported as module
is_main_program = __name__ == "__main__"

if is_main_program:
    # Read and set environment variables from .env file
    load_dotenv()

github_token = os.getenv("GITHUB_TOKEN")

g = Github(github_token, per_page=100)


def print_limits():
    """Print rate limits for Github API."""
    remaining, limit = g.rate_limiting
    resets_at = datetime.fromtimestamp(g.rate_limiting_resettime)
    print(f"Limits: {remaining}/{limit} {resets_at}")


def serialize_comment(review_id, comment):
    if comment.in_reply_to_id is None:
        return {
            "rw_id": review_id,
            "cm_body": comment.body,
            "cm_creation_time": comment.created_at.isoformat(),
            "cm_id": comment.id,
            "cm_user": comment.user.login,
        }


def serialize_review(pull_request_id, review):
    return {
        "pr_id": pull_request_id,
        "rw_id": review.id,
        "rw_user": review.user.login,
        "submitted_at": review.submitted_at.isoformat(),
        "rw_state": review.state,
        "rw_body": review.body,
    }


def serialize_pull_request(pull_request, assigned_reviewers):
    return {
        "base_branch": pull_request.base.ref,
        "created_at": pull_request.created_at.isoformat(),
        "is_draft": pull_request.draft,
        "pr_id": pull_request.id,
        "merged_at": pull_request.merged_at.isoformat()
        if pull_request.merged_at
        else None,
        "pr_state": pull_request.state,
        "created_by": pull_request.user.login,
        "assigned_reviewers": list(map(lambda user: user.login, assigned_reviewers)),
    }


def get_data(owner, repository_name):
    """
    Get serialized data from GitHub.

    Data includes info about pull requests, assigned reviewers, their reviews and comments
    associated with reviews from given repository.

        Parameters:
            owner (str): Repository owner
            repository_name (str): Repository name

        Returns:
            pull_requests (list): Pull requests data with assigned reviewers
            reviews (list): Reviews data
            comments (list): Review comments data
    """
    repository = g.get_repo(f"{owner}/{repository_name}")

    pull_requests = []
    reviews = []
    comments = []

    for index, pull_request in enumerate(
        repository.get_pulls(
            state="closed", sort="created", direction="desc", base="master"
        )[:400]
    ):
        review_requests = pull_request.get_review_requests()
        pull_requests.append(serialize_pull_request(pull_request, review_requests[0]))

        for review in pull_request.get_reviews():
            reviews.append(serialize_review(pull_request.id, review))

            for comment in pull_request.get_single_review_comments(review.id):
                serialized_comment = serialize_comment(review.id, comment)
                if serialized_comment is not None:
                    comments.append(serialized_comment)
        print(f"Pull request {index} is appended")
    return (pull_requests, reviews, comments)


def export_to_json(name, data):
    """
    Export data to a separate directory as JSON file.

        Parameters:
            name (str): Filename without extension
            data (*): Serializeable data
    """
    filename = f"data/{name}.json"
    with open(filename, "w") as file:
        json.dump(data, file)
    print(f"Data exported to '{filename}'")


if is_main_program:
    # Test using data from facebook/react
    pull_requests, reviews, comments = get_data("facebook", "react")

    export_to_json("pull_requests", pull_requests)
    export_to_json("reviews", reviews)
    export_to_json("comments", comments)

    print_limits()
