from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from postgrest import APIError
from supabase import StorageException

from app.core.config import settings
from app.services import storage


def run_async(coro):
    """Helper to run a coroutine that contains synchronous body without loopback sockets."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value


def test_upload_default_settings():
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_client.storage.from_.return_value = mock_bucket
    mock_bucket.get_public_url.return_value = "https://example.com/images/dish1.jpg"

    with patch.object(storage, "get_supabase_client", return_value=mock_client):
        url = run_async(storage.upload_image_to_storage("dish1.jpg", b"fake_content"))

    assert url == "https://example.com/images/dish1.jpg"
    mock_client.storage.from_.assert_called_with(settings.SUPABASE_BUCKET_NAME)
    mock_bucket.upload.assert_called_once_with(
        path=f"{settings.SUPABASE_STORAGE_PATH}/dish1.jpg",
        file=b"fake_content",
        file_options={"content-type": "image/jpeg"},
    )
    mock_bucket.get_public_url.assert_called_with(f"{settings.SUPABASE_STORAGE_PATH}/dish1.jpg")


def test_upload_custom_bucket_and_folder():
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_client.storage.from_.return_value = mock_bucket
    mock_bucket.get_public_url.return_value = "https://example.com/avatars/user.png"

    with patch.object(storage, "get_supabase_client", return_value=mock_client):
        url = run_async(
            storage.upload_image_to_storage(
                "user.png",
                b"fake_content",
                bucket_name="custom_bucket",
                folder="avatars",
                content_type="image/png",
            )
        )

    assert url == "https://example.com/avatars/user.png"
    mock_client.storage.from_.assert_called_with("custom_bucket")
    mock_bucket.upload.assert_called_once_with(
        path="avatars/user.png",
        file=b"fake_content",
        file_options={"content-type": "image/png"},
    )


def test_upload_path_formatting():
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_client.storage.from_.return_value = mock_bucket
    mock_bucket.get_public_url.return_value = "https://example.com/test.jpg"

    with patch.object(storage, "get_supabase_client", return_value=mock_client):
        # Folder with leading and trailing slashes
        run_async(
            storage.upload_image_to_storage(
                "test.jpg",
                b"fake_content",
                folder="/banners/",
            )
        )
        assert mock_bucket.upload.call_args.kwargs["path"] == "banners/test.jpg"

        # Empty folder (root of bucket)
        run_async(
            storage.upload_image_to_storage(
                "test.jpg",
                b"fake_content",
                folder="",
            )
        )
        assert mock_bucket.upload.call_args.kwargs["path"] == "test.jpg"


def test_upload_storage_exception():
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_client.storage.from_.return_value = mock_bucket
    mock_bucket.upload.side_effect = StorageException({"message": "Bucket not found"})

    with patch.object(storage, "get_supabase_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc_info:
            run_async(storage.upload_image_to_storage("test.jpg", b"fake_content"))
        assert exc_info.value.status_code == 400
        assert "Storage error: Bucket not found" in exc_info.value.detail


def test_upload_api_error():
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_client.storage.from_.return_value = mock_bucket
    mock_bucket.upload.side_effect = APIError({"message": "Access denied"})

    with patch.object(storage, "get_supabase_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc_info:
            run_async(storage.upload_image_to_storage("test.jpg", b"fake_content"))
        assert exc_info.value.status_code == 500
