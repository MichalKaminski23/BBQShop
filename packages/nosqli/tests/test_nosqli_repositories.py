"""Te same scenariusze logowania uruchamiane na obu wariantach."""

import pytest
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from bbq_db.mongo import USERS_COLLECTION
from bbq_nosqli.repository import UserRepository
from bbq_nosqli.secure import SecureUserRepository
from bbq_nosqli.vulnerable import VulnerableUserRepository

pytestmark = pytest.mark.integration

BOTH = pytest.mark.parametrize(
    "repository_cls",
    [VulnerableUserRepository, SecureUserRepository],
    ids=["vulnerable", "secure"],
)

# Operator Mongo pasujący do dowolnego dokumentu.
OPERATOR: dict[str, None] = {"$ne": None}


def _users(mongo_db: AsyncDatabase[dict[str, object]]) -> AsyncCollection[dict[str, object]]:
    return mongo_db[USERS_COLLECTION]


@BOTH
async def test_valid_credentials_authenticate(
    mongo_db: AsyncDatabase[dict[str, object]], repository_cls: type[UserRepository]
) -> None:
    user = await repository_cls(_users(mongo_db)).authenticate("admin", "Admin123!")

    assert user is not None
    assert user["role"] == "admin"


@BOTH
async def test_wrong_password_is_rejected(
    mongo_db: AsyncDatabase[dict[str, object]], repository_cls: type[UserRepository]
) -> None:
    user = await repository_cls(_users(mongo_db)).authenticate("admin", "zle-haslo")

    assert user is None


@BOTH
async def test_unknown_user_is_rejected(
    mongo_db: AsyncDatabase[dict[str, object]], repository_cls: type[UserRepository]
) -> None:
    user = await repository_cls(_users(mongo_db)).authenticate("nieistnieje", "x")

    assert user is None


async def test_operator_injection_bypasses_login_in_vulnerable(
    mongo_db: AsyncDatabase[dict[str, object]],
) -> None:
    user = await VulnerableUserRepository(_users(mongo_db)).authenticate(OPERATOR, OPERATOR)

    assert user is not None  # zalogowany bez znajomości loginu i hasła


async def test_operator_injection_is_blocked_in_secure(
    mongo_db: AsyncDatabase[dict[str, object]],
) -> None:
    repo = SecureUserRepository(_users(mongo_db))

    assert await repo.authenticate(OPERATOR, OPERATOR) is None
    assert await repo.authenticate(OPERATOR, "Admin123!") is None
