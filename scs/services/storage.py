"""
SCS Storage Service

Provides S3-compatible file storage functionality.
"""

import mimetypes
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Dict, List, Optional, Union

if TYPE_CHECKING:
    from ..client import SCS


class StorageReference:
    """
    Reference to a file in storage.

    Usage:
        file_ref = scs.storage.ref('file-id')

        # Get metadata
        metadata = file_ref.get_metadata()

        # Download file
        content = file_ref.download()

        # Download to file
        file_ref.download_to_file('./local_file.png')

        # Get download URL
        url = file_ref.get_download_url()

        # Delete file
        file_ref.delete()
    """

    def __init__(self, scs: "SCS", file_id: str):
        """
        Initialize storage reference.

        Args:
            scs: SCS client instance
            file_id: File ID
        """
        self._scs = scs
        self._file_id = file_id

    @property
    def id(self) -> str:
        """Get the file ID."""
        return self._file_id

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get file metadata.

        Returns:
            File metadata object
        """
        return self._scs.request(f"/api/storage/files/{self._file_id}/metadata")

    def download(self) -> bytes:
        """
        Download file content.

        Returns:
            File content as bytes
        """
        return self._scs.download_request(f"/api/storage/files/{self._file_id}")

    def download_to_file(self, path: Union[str, Path]) -> None:
        """
        Download file to local path.

        Args:
            path: Local file path
        """
        content = self.download()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def get_download_url(self) -> str:
        """
        Get the download URL for the file.

        Returns:
            Download URL
        """
        return f"{self._scs.base_url}/api/storage/files/{self._file_id}"

    def delete(self) -> Dict[str, Any]:
        """
        Delete the file.

        Returns:
            Success message
        """
        return self._scs.request(
            f"/api/storage/files/{self._file_id}",
            method="DELETE",
        )


class StorageService:
    """
    Storage service for file management.

    Usage:
        # Upload from file path
        file_info = scs.storage.upload('./image.png')

        # Upload from bytes
        file_info = scs.storage.upload_bytes(
            data=image_bytes,
            filename='image.png',
            content_type='image/png'
        )

        # Upload with folder
        file_info = scs.storage.upload('./doc.pdf', folder='documents')

        # List files
        files = scs.storage.list_files()

        # Get file reference
        file_ref = scs.storage.ref('file-id')

        # Create folder
        scs.storage.create_folder('my-folder')

        # Delete folder
        scs.storage.delete_folder('my-folder')
    """

    def __init__(self, scs: "SCS"):
        self._scs = scs

    def ref(self, file_id: str) -> StorageReference:
        """
        Get a reference to a file.

        Args:
            file_id: File ID

        Returns:
            StorageReference
        """
        return StorageReference(self._scs, file_id)

    def upload(
        self,
        file_path: Union[str, Path],
        folder: Optional[str] = None,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a file from local path.

        Args:
            file_path: Path to file to upload
            folder: Optional folder path in storage
            filename: Optional custom filename (defaults to original)
            content_type: Optional content type (auto-detected if not provided)

        Returns:
            Uploaded file info
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine content type
        if not content_type:
            content_type, _ = mimetypes.guess_type(str(file_path))
            content_type = content_type or "application/octet-stream"

        # Determine filename
        upload_filename = filename or file_path.name

        # Prepare file tuple
        with open(file_path, "rb") as f:
            files = {
                "file": (upload_filename, f, content_type),
            }

            data = {}
            if folder:
                data["folder"] = folder

            return self._scs.upload_request(
                "/api/storage/upload",
                files=files,
                data=data if data else None,
            )

    def upload_bytes(
        self,
        data: Union[bytes, BinaryIO],
        filename: str,
        content_type: Optional[str] = None,
        folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload file from bytes or file-like object.

        Args:
            data: File content as bytes or file-like object
            filename: Filename for the uploaded file
            content_type: Content type (defaults to application/octet-stream)
            folder: Optional folder path in storage

        Returns:
            Uploaded file info
        """
        if not content_type:
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or "application/octet-stream"

        # Handle both bytes and file-like objects
        if isinstance(data, bytes):
            file_data = data
        else:
            file_data = data.read()

        files = {
            "file": (filename, file_data, content_type),
        }

        form_data = {}
        if folder:
            form_data["folder"] = folder

        return self._scs.upload_request(
            "/api/storage/upload",
            files=files,
            data=form_data if form_data else None,
        )

    def list_files(
        self,
        folder: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        List files in storage.

        Args:
            folder: Optional folder to list files from
            page: Page number
            limit: Items per page

        Returns:
            Paginated list of files
        """
        params = {
            "page": page,
            "limit": limit,
        }

        if folder:
            params["folder"] = folder

        return self._scs.request("/api/storage/files", params=params)

    def get_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get file metadata by ID.

        Args:
            file_id: File ID

        Returns:
            File metadata
        """
        return self.ref(file_id).get_metadata()

    def download(self, file_id: str) -> bytes:
        """
        Download file by ID.

        Args:
            file_id: File ID

        Returns:
            File content as bytes
        """
        return self.ref(file_id).download()

    def download_to_file(
        self,
        file_id: str,
        path: Union[str, Path],
    ) -> None:
        """
        Download file to local path.

        Args:
            file_id: File ID
            path: Local file path
        """
        self.ref(file_id).download_to_file(path)

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete a file.

        Args:
            file_id: File ID

        Returns:
            Success message
        """
        return self.ref(file_id).delete()

    def create_folder(self, path: str) -> Dict[str, Any]:
        """
        Create a folder.

        Args:
            path: Folder path

        Returns:
            Created folder info
        """
        return self._scs.request(
            "/api/storage/folders",
            method="POST",
            body={"path": path},
        )

    def delete_folder(self, path: str) -> Dict[str, Any]:
        """
        Delete a folder and its contents.

        Args:
            path: Folder path

        Returns:
            Success message
        """
        return self._scs.request(
            f"/api/storage/folders/{path}",
            method="DELETE",
        )
