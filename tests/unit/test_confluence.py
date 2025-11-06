"""Unit tests for confluence module."""

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from confluence_markdown_exporter.confluence import Page


class TestPageExport:
    """Test cases for Page export methods."""

    @patch("confluence_markdown_exporter.confluence.save_file")
    @patch("confluence_markdown_exporter.confluence.settings")
    def test_export_html_format(self, mock_settings, mock_save_file):
        """Test exporting page in HTML format."""
        # Setup mock settings
        mock_settings.export.export_format = "html"
        mock_settings.export.page_breadcrumbs = False
        mock_settings.export.output_path = Path("/tmp/output")

        # Create mock page
        page = MagicMock(spec=Page)
        page.title = "Test Page"
        page.html = "<h1>Test Page</h1><p>Content</p>"
        page.export_path = Path("test/page.html")
        page.labels = []
        page.ancestors = []

        # Call export_html directly
        Page.export_html(page)

        # Verify save_file was called with correct parameters
        mock_save_file.assert_called_once()
        assert page.html in str(mock_save_file.call_args)

    @patch("confluence_markdown_exporter.confluence.settings")
    def test_file_extension_html(self, mock_settings):
        """Test file extension returns .html when format is html."""
        mock_settings.export.export_format = "html"

        page = MagicMock(spec=Page)
        extension = Page.file_extension.fget(page)

        assert extension == ".html"

    @patch("confluence_markdown_exporter.confluence.settings")
    def test_file_extension_markdown(self, mock_settings):
        """Test file extension returns .md when format is markdown."""
        mock_settings.export.export_format = "markdown"

        page = MagicMock(spec=Page)
        extension = Page.file_extension.fget(page)

        assert extension == ".md"
