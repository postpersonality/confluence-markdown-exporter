"""Integration test for attachment export without overwrites."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from confluence_markdown_exporter.confluence import Attachment, Space, User, Version


class TestAttachmentExportIntegration:
    """Integration tests for attachment export."""

    @patch("confluence_markdown_exporter.confluence.Page.from_id")
    @patch("confluence_markdown_exporter.confluence.confluence")
    @patch("confluence_markdown_exporter.confluence.settings")
    def test_multiple_attachments_no_overwrite(self, mock_settings, mock_confluence, mock_page_from_id):
        """Test that multiple attachments with empty file_id don't overwrite each other."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            mock_settings.export.output_path = output_path
            mock_settings.export.attachment_path = "attachments/{attachment_file_id}{attachment_extension}"
            
            # Mock Page.from_id to avoid API calls
            mock_page = MagicMock()
            mock_page.title = "Test Page"
            mock_page_from_id.return_value = mock_page
            
            # Create mock user and version
            mock_user = User(
                account_id="test-account-id",
                username="testuser",
                display_name="Test User",
                public_name="Test User",
                email="test@example.com",
            )
            
            mock_version = Version(
                number=1,
                by=mock_user,
                when="2024-01-01T00:00:00.000Z",
                friendly_when="Jan 01, 2024",
            )
            
            # Create mock space
            mock_space = Space(
                key="TEST",
                name="Test Space",
                description="Test Description",
                homepage=123456,
            )
            
            # Create two attachments with empty file_id but same extension
            attachment1 = Attachment(
                id="111",
                title="First Document",
                space=mock_space,
                file_size=1024,
                media_type="application/pdf",
                media_type_description="PDF",
                file_id="",  # Empty file_id
                collection_name="attachments",
                download_link="/download/1",
                comment="",
                ancestors=[],
                version=mock_version,
            )
            
            attachment2 = Attachment(
                id="222",
                title="Second Document",
                space=mock_space,
                file_size=2048,
                media_type="application/pdf",
                media_type_description="PDF",
                file_id="",  # Empty file_id
                collection_name="attachments",
                download_link="/download/2",
                comment="",
                ancestors=[],
                version=mock_version,
            )
            
            # Mock HTTP responses
            mock_response1 = MagicMock()
            mock_response1.content = b"PDF content 1"
            mock_response1.raise_for_status = MagicMock()
            
            mock_response2 = MagicMock()
            mock_response2.content = b"PDF content 2"
            mock_response2.raise_for_status = MagicMock()
            
            mock_confluence._session.get.side_effect = [mock_response1, mock_response2]
            mock_confluence.url = ""
            
            # Export both attachments
            attachment1.export()
            attachment2.export()
            
            # Verify both files exist
            files = list(output_path.glob("**/*.pdf"))
            assert len(files) == 2, f"Expected 2 PDF files, found {len(files)}: {files}"
            
            # Verify filenames are different
            filenames = {f.name for f in files}
            assert len(filenames) == 2, "Filenames should be unique"
            
            # Verify content is different
            contents = {f.read_bytes() for f in files}
            assert len(contents) == 2, "File contents should be different"
            
            # Verify expected filenames
            assert "111_First Document.pdf" in filenames
            assert "222_Second Document.pdf" in filenames
