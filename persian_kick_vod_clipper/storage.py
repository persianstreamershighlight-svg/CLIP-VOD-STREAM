from __future__ import annotations

from pathlib import Path


class GoogleDriveUploader:
    def __init__(self, credentials: Path, root_folder_id: str):
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        scopes = ["https://www.googleapis.com/auth/drive.file"]
        creds = Credentials.from_service_account_file(str(credentials), scopes=scopes)
        self.service = build("drive", "v3", credentials=creds, cache_discovery=False)
        self.root_folder_id = root_folder_id

    def upload(self, path: Path, parent_id: str | None = None) -> str:
        from googleapiclient.http import MediaFileUpload
        metadata = {"name": path.name, "parents": [parent_id or self.root_folder_id]}
        result = self.service.files().create(body=metadata, media_body=MediaFileUpload(str(path), resumable=True), fields="id,webViewLink").execute()
        return result.get("webViewLink") or f"https://drive.google.com/file/d/{result['id']}/view"

