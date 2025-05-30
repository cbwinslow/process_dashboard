"""
Template selection and management UI for Process Dashboard.

Provides interface for browsing, applying, and customizing configuration templates.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, Horizontal, Grid
from textual.widgets import (
    Button, Static, DataTable, Label, Input, TextArea,
    RadioSet, RadioButton, OptionList
)
from textual.message import Message
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel

from typing import Dict, Any, Optional
import logging
from pathlib import Path

from ..config.templates import ConfigurationTemplate, TEMPLATES
from ..config.validators import ConfigValidator

logger = logging.getLogger("dashboard.ui.templates")

class TemplateScreen(Screen):
    """Template selection and management screen."""

    BINDINGS = [
        Binding("escape", "close_templates", "Close", show=True),
        Binding("ctrl+s", "save_template", "Save Template", show=True),
        Binding("ctrl+a", "apply_template", "Apply Template", show=True),
        Binding("ctrl+e", "export_template", "Export", show=True),
        Binding("ctrl+i", "import_template", "Import", show=True),
    ]

    DEFAULT_CSS = """
    TemplateScreen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
        padding: 1;
        background: $background;
    }

    #template-list {
        height: 100%;
        border: solid $accent;
    }

    #template-details {
        height: 100%;
        border: solid $accent;
    }

    .template-section {
        margin: 1;
        padding: 1;
        border: solid $accent;
    }

    DataTable {
        height: auto;
        max-height: 50%;
    }

    TextArea {
        height: 30%;
    }

    #preview-area {
        height: 40%;
        border: solid $accent;
        margin-top: 1;
    }

    .button-row {
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 1;
    }

    .built-in {
        color: $accent;
    }

    .custom {
        color: $text;
    }

    #error-message {
        color: $error;
        margin: 1;
    }

    #success-message {
        color: $success;
        margin: 1;
    }
    """

    class TemplateSelected(Message):
        """Message emitted when template is selected."""
        def __init__(self, template_id: str, config: Dict[str, Any]):
            self.template_id = template_id
            self.config = config
            super().__init__()

    def __init__(self, config_dir: Path):
        """Initialize template screen.
        
        Args:
            config_dir: Configuration directory path
        """
        super().__init__()
        self.template_manager = ConfigurationTemplate(config_dir)
        self.selected_template: Optional[str] = None
        self.current_config: Optional[Dict[str, Any]] = None
        self.modified = False

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Template list panel
        with Vertical(id="template-list"):
            yield Label("Configuration Templates")
            yield DataTable(id="templates-table")
            
            with Vertical(classes="template-section"):
                yield Label("Template Actions")
                with Horizontal(classes="button-row"):
                    yield Button("Apply", variant="primary", id="apply")
                    yield Button("Save As", id="save-as")
                    yield Button("Delete", variant="error", id="delete")
                    yield Button("Export", id="export")

        # Template details panel
        with Vertical(id="template-details"):
            yield Label("Template Details")
            
            with Grid(id="template-info"):
                yield Label("Name:")
                yield Input(id="template-name")
                yield Label("Description:")
                yield TextArea(id="template-description")
            
            with Vertical(classes="template-section"):
                yield Label("Customization")
                yield RadioSet(
                    RadioButton("Use as-is", value="as-is"),
                    RadioButton("Customize", value="customize"),
                    id="template-mode"
                )
            
            with Vertical(id="preview-area"):
                yield Label("Preview")
                yield Static(id="config-preview")
            
            yield Static(id="error-message")
            yield Static(id="success-message")

    def on_mount(self) -> None:
        """Handle screen mount."""
        self.setup_templates_table()
        self.load_templates()

    def setup_templates_table(self) -> None:
        """Set up templates data table."""
        table = self.query_one("#templates-table", DataTable)
        table.add_columns("Name", "Type", "Description")

    def load_templates(self) -> None:
        """Load and display available templates."""
        try:
            table = self.query_one("#templates-table", DataTable)
            table.clear()
            
            # Load templates
            templates = self.template_manager.get_template_list()
            
            # Add to table
            for template in templates:
                template_id = template["id"]
                row_key = str(template_id)
                style = "built-in" if template["built_in"] else "custom"
                
                table.add_row(
                    template["name"],
                    "Built-in" if template["built_in"] else "Custom",
                    template["description"],
                    key=row_key,
                    classes=style
                )
            
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            self.show_error("Failed to load templates")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle template selection."""
        try:
            template_id = event.row_key.value
            self.selected_template = template_id
            
            # Load template
            config = self.template_manager.load_template(template_id)
            if config:
                self.current_config = config
                self.show_template_details(template_id, config)
            
        except Exception as e:
            logger.error(f"Failed to select template: {e}")
            self.show_error("Failed to load template details")

    def show_template_details(self, template_id: str, config: Dict[str, Any]) -> None:
        """Show template details and preview.
        
        Args:
            template_id: Template identifier
            config: Template configuration
        """
        try:
            # Get template info
            templates = self.template_manager.get_template_list()
            template = next(t for t in templates if t["id"] == template_id)
            
            # Update details
            self.query_one("#template-name", Input).value = template["name"]
            self.query_one("#template-description", TextArea).text = template["description"]
            
            # Show preview
            preview = self.query_one("#config-preview", Static)
            preview.update(Panel(
                Text(str(config), style="bold"),
                title="Configuration Preview",
                border_style="green"
            ))
            
        except Exception as e:
            logger.error(f"Failed to show template details: {e}")
            self.show_error("Failed to display template details")

    def action_apply_template(self) -> None:
        """Apply selected template."""
        if not self.selected_template or not self.current_config:
            self.show_error("No template selected")
            return
        
        try:
            # Check if customization is needed
            mode = self.query_one("#template-mode", RadioSet).pressed_button.value
            
            if mode == "customize":
                # TODO: Open configuration editor with template
                pass
            else:
                # Validate configuration
                validator = ConfigValidator()
                if not validator.validate_display_config(self.current_config.get("display", {})):
                    self.show_error("Invalid display configuration")
                    return
                if not validator.validate_process_config(self.current_config.get("process", {})):
                    self.show_error("Invalid process configuration")
                    return
                if not validator.validate_resource_config(self.current_config.get("resources", {})):
                    self.show_error("Invalid resource configuration")
                    return
                
                # Apply template
                self.post_message(self.TemplateSelected(
                    self.selected_template,
                    self.current_config
                ))
                self.show_success("Template applied successfully")
                
        except Exception as e:
            logger.error(f"Failed to apply template: {e}")
            self.show_error("Failed to apply template")

    def action_save_template(self) -> None:
        """Save current configuration as template."""
        if not self.current_config:
            self.show_error("No configuration to save")
            return
        
        try:
            name = self.query_one("#template-name", Input).value
            description = self.query_one("#template-description", TextArea).text
            
            if not name:
                self.show_error("Template name required")
                return
            
            # Save template
            if self.template_manager.save_template(name, self.current_config, description):
                self.show_success("Template saved successfully")
                self.load_templates()
            else:
                self.show_error("Failed to save template")
            
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            self.show_error("Failed to save template")

    def action_delete_template(self) -> None:
        """Delete selected template."""
        if not self.selected_template:
            self.show_error("No template selected")
            return
        
        try:
            if self.template_manager.delete_template(self.selected_template):
                self.show_success("Template deleted successfully")
                self.load_templates()
                self.selected_template = None
                self.current_config = None
            else:
                self.show_error("Cannot delete built-in template")
            
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            self.show_error("Failed to delete template")

    def action_export_template(self) -> None:
        """Export selected template."""
        if not self.selected_template or not self.current_config:
            self.show_error("No template selected")
            return
        
        try:
            # Get template name
            name = self.query_one("#template-name", Input).value
            export_file = Path.home() / f"{name.lower().replace(' ', '_')}_template.yaml"
            
            # Export template
            if self.template_manager.export_config(self.current_config, export_file):
                self.show_success(f"Template exported to: {export_file}")
            else:
                self.show_error("Failed to export template")
            
        except Exception as e:
            logger.error(f"Failed to export template: {e}")
            self.show_error("Failed to export template")

    def action_import_template(self) -> None:
        """Import template from file."""
        try:
            # TODO: Add file selection dialog
            import_file = Path.home() / "imported_template.yaml"
            
            if not import_file.exists():
                self.show_error("Import file not found")
                return
            
            # Import configuration
            config = self.template_manager.import_config(import_file)
            if config:
                self.current_config = config
                self.show_template_details("imported", config)
                self.show_success("Template imported successfully")
            else:
                self.show_error("Failed to import template")
            
        except Exception as e:
            logger.error(f"Failed to import template: {e}")
            self.show_error("Failed to import template")

    def show_error(self, message: str) -> None:
        """Show error message.
        
        Args:
            message: Error message
        """
        self.query_one("#error-message").update(message)
        self.query_one("#success-message").update("")

    def show_success(self, message: str) -> None:
        """Show success message.
        
        Args:
            message: Success message
        """
        self.query_one("#success-message").update(message)
        self.query_one("#error-message").update("")

    def action_close_templates(self) -> None:
        """Close template screen."""
        self.app.pop_screen()
