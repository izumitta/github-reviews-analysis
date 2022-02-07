import pytest
from datetime import datetime
from asserts import assert_dict_equal, assert_equal
from get_data import serialize_comment, serialize_review, serialize_pull_request


class User:
    def __init__(self, login="peepoo"):
        self.login = login


class Comment:
    def __init__(self, in_reply_to_id=None):
        self.in_reply_to_id = in_reply_to_id
        self.body = "asdfg"
        self.created_at = datetime(2022, 12, 12)
        self.id = 3456
        self.user = User()


class Review:
    def __init__(self, body=""):
        self.id = 234
        self.user = User()
        self.submitted_at = datetime(2022, 12, 12)
        self.state = "APPROVED"
        self.body = body


class PullRequestPart:
    def __init__(self):
        self.ref = "master"


class PullRequest:
    def __init__(self, merged_at=None):
        self.base = PullRequestPart()
        self.created_at = datetime(2022, 12, 12)
        self.draft = False
        self.id = 164
        self.merged_at = merged_at
        self.state = "closed"
        self.user = User()


class TestSerializeComment:
    def test_not_in_reply(self):
        expected = {
            "rw_id": 164,
            "cm_body": "asdfg",
            "cm_creation_time": "2022-12-12T00:00:00",
            "cm_id": 3456,
            "cm_user": "peepoo",
        }
        actual = serialize_comment(164, Comment())
        assert_dict_equal(actual, expected)

    def test_in_reply(self):
        expected = None
        actual = serialize_comment(164, Comment(123))
        assert_equal(actual, expected)


class TestSerializeReview:
    def test_review_with_body(self):
        expected = {
            "pr_id": 164,
            "rw_id": 234,
            "rw_user": "peepoo",
            "submitted_at": "2022-12-12T00:00:00",
            "rw_state": "APPROVED",
            "rw_body": "asdfgh",
        }
        actual = serialize_review(164, Review(body="asdfgh"))
        assert_dict_equal(actual, expected)

    def test_review_no_body(self):
        expected = {
            "pr_id": 164,
            "rw_id": 234,
            "rw_user": "peepoo",
            "submitted_at": "2022-12-12T00:00:00",
            "rw_state": "APPROVED",
            "rw_body": None,
        }
        actual = serialize_review(164, Review())
        assert_dict_equal(actual, expected)


class TestSerializePullRequest:
    def test_merged(self):
        expected = {
            "base_branch": "master",
            "created_at": "2022-12-12T00:00:00",
            "is_draft": False,
            "pr_id": 164,
            "merged_at": "2022-12-12T00:00:00",
            "pr_state": "closed",
            "created_by": "peepoo",
            "assigned_reviewers": ["john", "jane"],
        }
        actual = serialize_pull_request(
            PullRequest(merged_at=datetime(2022, 12, 12)), [User("john"), User("jane")]
        )
        assert_dict_equal(actual, expected)

    def test_not_merged(self):
        expected = {
            "base_branch": "master",
            "created_at": "2022-12-12T00:00:00",
            "is_draft": False,
            "pr_id": 164,
            "merged_at": None,
            "pr_state": "closed",
            "created_by": "peepoo",
            "assigned_reviewers": ["john", "jane"],
        }
        actual = serialize_pull_request(PullRequest(), [User("john"), User("jane")])
        assert_dict_equal(actual, expected)
