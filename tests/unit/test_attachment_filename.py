"""Unit tests for Attachment.filename property."""

from unittest.mock import MagicMock, patch

import pytest

from confluence_markdown_exporter.confluence import Attachment, Space, User, Version


class TestAttachmentFilename:
    """Test cases for Attachment filename generation."""

    def create_mock_attachment(
        self,
        attachment_id: str = "123456",
        title: str = "test-file",
        file_id: str = "abc-def-guid",
        media_type: str = "image/png",
    ) -> Attachment:
        """Create a mock Attachment object for testing."""
        # Create minimal User for Version
        mock_user = User(
            account_id="test-account-id",
            username="testuser",
            display_name="Test User",
            public_name="Test User",
            email="test@example.com",
        )
        
        # Create minimal Version
        mock_version = Version(
            number=1,
            by=mock_user,
            when="2024-01-01T00:00:00.000Z",
            friendly_when="Jan 01, 2024",
        )
        
        # Create minimal Space
        mock_space = Space(
            key="TEST",
            name="Test Space",
            description="Test Description",
            homepage=123456,
        )
        
        # Create minimal attachment
        attachment = Attachment(
            id=attachment_id,
            title=title,
            space=mock_space,
            file_size=1024,
            media_type=media_type,
            media_type_description="PNG image",
            file_id=file_id,
            collection_name="attachments",
            download_link="/download/attachments/123456/test.png",
            comment="",
            ancestors=[],
            version=mock_version,
        )
        return attachment

    def test_filename_with_file_id(self):
        """Test filename generation when file_id is present (Confluence Cloud)."""
        attachment = self.create_mock_attachment(
            file_id="abc-def-guid-1234",
            title="My Document",
            media_type="application/pdf",
        )
        
        assert attachment.filename == "abc-def-guid-1234.pdf"

    def test_filename_without_file_id(self):
        """Test filename generation when file_id is empty (Confluence Server)."""
        attachment = self.create_mock_attachment(
            attachment_id="645208921",
            file_id="",  # Empty file_id
            title="My Document",
            media_type="application/pdf",
        )
        
        assert attachment.filename == "645208921_My Document.pdf"

    def test_filename_without_file_id_and_special_chars(self):
        """Test filename sanitization when file_id is empty."""
        with patch("confluence_markdown_exporter.confluence.sanitize_filename") as mock_sanitize:
            mock_sanitize.return_value = "My_Document_Test"
            
            attachment = self.create_mock_attachment(
                attachment_id="123",
                file_id="",
                title="My: Document? Test!",
                media_type="application/pdf",
            )
            
            assert attachment.filename == "123_My_Document_Test.pdf"
            mock_sanitize.assert_called_once_with("My: Document? Test!")

    def test_filename_without_file_id_empty_title(self):
        """Test filename when both file_id is empty and title is empty."""
        attachment = self.create_mock_attachment(
            attachment_id="999",
            file_id="",
            title="",
            media_type="image/png",
        )
        
        assert attachment.filename == "999.png"

    def test_filename_removes_duplicate_extension(self):
        """Test that duplicate extensions are removed from title."""
        attachment = self.create_mock_attachment(
            attachment_id="555",
            file_id="",
            title="document.pdf",
            media_type="application/pdf",
        )
        
        # Should be "555_document.pdf" not "555_document.pdf.pdf"
        assert attachment.filename == "555_document.pdf"
        assert attachment.filename.count(".pdf") == 1

    def test_filename_uniqueness_same_title_different_ids(self):
        """Test that attachments with same title but different IDs get unique filenames."""
        attachment1 = self.create_mock_attachment(
            attachment_id="111",
            file_id="",
            title="report",
            media_type="application/pdf",
        )
        
        attachment2 = self.create_mock_attachment(
            attachment_id="222",
            file_id="",
            title="report",
            media_type="application/pdf",
        )
        
        assert attachment1.filename != attachment2.filename
        assert attachment1.filename == "111_report.pdf"
        assert attachment2.filename == "222_report.pdf"

    @pytest.mark.parametrize(
        "media_type,expected_ext",
        [
            ("image/png", ".png"),
            ("image/jpeg", ".jpg"),  # mimetypes.guess_extension returns .jpg for image/jpeg
            ("application/pdf", ".pdf"),
            ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
            ("text/plain", ".txt"),
        ],
    )
    def test_filename_different_media_types(self, media_type: str, expected_ext: str):
        """Test filename generation for different media types."""
        attachment = self.create_mock_attachment(
            attachment_id="777",
            file_id="",
            title="file",
            media_type=media_type,
        )
        
        assert attachment.filename.endswith(expected_ext)
        assert attachment.filename.startswith("777_file")
