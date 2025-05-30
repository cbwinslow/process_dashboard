"""
Notification templates for Process Dashboard alerts.

Provides customizable templates for different notification channels and alert types.
"""

from typing import Dict, Any
import yaml
from pathlib import Path
import logging
import jinja2
from datetime import datetime

logger = logging.getLogger("dashboard.config.templates")

# Default templates for different formats
DEFAULT_TEMPLATES = {
    "basic": {
        "name": "Basic Alert",
        "subject": "[{{ severity }}] Process Dashboard Alert",
        "body": """
Alert: {{ message }}
Rule: {{ rule_name }}
Severity: {{ severity }}
Time: {{ created_at }}
Value: {{ value }} {{ condition }} {{ threshold }}
""",
        "format": "text"
    },
    "detailed": {
        "name": "Detailed Alert",
        "subject": "[Process Dashboard] {{ severity }} Alert - {{ rule_name }}",
        "body": """
Alert Details
============

Rule:     {{ rule_name }}
Severity: {{ severity }}
Status:   {{ status }}
Time:     {{ created_at }}

Metrics
-------
Current Value: {{ value }}
Threshold:    {{ threshold }} ({{ condition }})
Trend:        {{ trend }}

Message
-------
{{ message }}

{% if related_alerts %}
Related Alerts
-------------
{% for alert in related_alerts %}
- {{ alert.created_at }}: {{ alert.message }}
{% endfor %}
{% endif %}

{% if recommendations %}
Recommendations
--------------
{% for rec in recommendations %}
- {{ rec }}
{% endfor %}
{% endif %}
""",
        "format": "text"
    },
    "html_alert": {
        "name": "HTML Alert",
        "subject": "[Process Dashboard] {{ severity }} Alert - {{ rule_name }}",
        "body": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 10px; border-radius: 5px; }
        .severity { font-weight: bold; }
        .severity-warning { color: #f0ad4e; }
        .severity-error { color: #d9534f; }
        .severity-critical { color: #9c27b0; }
        .metrics { margin: 15px 0; }
        .metric { margin: 5px 0; }
        .related { margin-top: 20px; border-top: 1px solid #eee; }
        .recommendations { margin-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Process Dashboard Alert</h2>
        <p class="severity severity-{{ severity|lower }}">{{ severity }} Alert</p>
    </div>

    <div class="details">
        <h3>Alert Details</h3>
        <p><strong>Rule:</strong> {{ rule_name }}</p>
        <p><strong>Status:</strong> {{ status }}</p>
        <p><strong>Time:</strong> {{ created_at }}</p>
    </div>

    <div class="metrics">
        <h3>Metrics</h3>
        <div class="metric">
            <strong>Current Value:</strong> {{ value }}<br>
            <strong>Threshold:</strong> {{ threshold }} ({{ condition }})<br>
            <strong>Trend:</strong> {{ trend }}
        </div>
    </div>

    <div class="message">
        <h3>Message</h3>
        <p>{{ message }}</p>
    </div>

    {% if related_alerts %}
    <div class="related">
        <h3>Related Alerts</h3>
        <ul>
        {% for alert in related_alerts %}
            <li>{{ alert.created_at }}: {{ alert.message }}</li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}

    {% if recommendations %}
    <div class="recommendations">
        <h3>Recommendations</h3>
        <ul>
        {% for rec in recommendations %}
            <li>{{ rec }}</li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}
</body>
</html>
""",
        "format": "html"
    },
    "slack": {
        "name": "Slack Alert",
        "subject": "Process Dashboard Alert",
        "body": {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "{{ severity }} Alert: {{ rule_name }}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "{{ message }}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Status:*\n{{ status }}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Time:*\n{{ created_at }}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Value:*\n{{ value }}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Threshold:*\n{{ threshold }} ({{ condition }})"
                        }
                    ]
                }
            ]
        },
        "format": "json"
    }
}

class TemplateManager:
    """Template management system."""

    def __init__(self, template_dir: Path):
        """Initialize template manager.
        
        Args:
            template_dir: Template directory path
        """
        self.template_dir = template_dir
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.templates = DEFAULT_TEMPLATES.copy()
        self.load_templates()

    def load_templates(self) -> None:
        """Load custom templates from directory."""
        try:
            for template_file in self.template_dir.glob("*.yaml"):
                with open(template_file) as f:
                    template = yaml.safe_load(f)
                    if self._validate_template(template):
                        self.templates[template["name"]] = template
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")

    def _validate_template(self, template: Dict[str, Any]) -> bool:
        """Validate template structure.
        
        Args:
            template: Template dictionary
            
        Returns:
            True if valid
        """
        required = {"name", "subject", "body", "format"}
        if not all(key in template for key in required):
            return False
        
        if template["format"] not in {"text", "html", "json", "markdown"}:
            return False
        
        return True

    def save_template(
        self,
        name: str,
        template: Dict[str, Any]
    ) -> bool:
        """Save custom template.
        
        Args:
            name: Template name
            template: Template dictionary
            
        Returns:
            True if successful
        """
        try:
            if not self._validate_template(template):
                raise ValueError("Invalid template structure")
            
            template_file = self.template_dir / f"{name}.yaml"
            with open(template_file, 'w') as f:
                yaml.safe_dump(template, f)
            
            self.templates[name] = template
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False

    def delete_template(self, name: str) -> bool:
        """Delete custom template.
        
        Args:
            name: Template name
            
        Returns:
            True if successful
        """
        try:
            if name in DEFAULT_TEMPLATES:
                return False
            
            template_file = self.template_dir / f"{name}.yaml"
            if template_file.exists():
                template_file.unlink()
            
            if name in self.templates:
                del self.templates[name]
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            return False

    def render_template(
        self,
        name: str,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Render notification template.
        
        Args:
            name: Template name
            context: Template context
            
        Returns:
            Rendered message
        """
        try:
            template = self.templates.get(name)
            if not template:
                template = DEFAULT_TEMPLATES["basic"]
            
            # Add utility functions to context
            context["format_date"] = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")
            context["format_number"] = lambda n: f"{n:,.2f}"
            
            # Render subject
            subject_template = jinja2.Template(template["subject"])
            subject = subject_template.render(context)
            
            # Render body
            if isinstance(template["body"], str):
                body_template = jinja2.Template(template["body"])
                body = body_template.render(context)
            else:
                # Handle structured templates (e.g., Slack blocks)
                body = self._render_structured(template["body"], context)
            
            return {
                "subject": subject,
                "body": body,
                "format": template["format"]
            }
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            return {
                "subject": "Alert",
                "body": str(context.get("message", "Alert")),
                "format": "text"
            }

    def _render_structured(
        self,
        template: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Render structured template.
        
        Args:
            template: Template structure
            context: Template context
            
        Returns:
            Rendered template
        """
        import json
        
        def render_value(value):
            if isinstance(value, str):
                return jinja2.Template(value).render(context)
            elif isinstance(value, dict):
                return {k: render_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [render_value(v) for v in value]
            return value
        
        rendered = render_value(template)
        return json.dumps(rendered, indent=2)

    def get_template_list(self) -> List[Dict[str, Any]]:
        """Get list of available templates.
        
        Returns:
            List of template information
        """
        return [
            {
                "name": name,
                "format": template["format"],
                "built_in": name in DEFAULT_TEMPLATES
            }
            for name, template in self.templates.items()
        ]

    def preview_template(
        self,
        name: str,
        sample_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Preview template with sample data.
        
        Args:
            name: Template name
            sample_data: Optional sample data
            
        Returns:
            Rendered preview
        """
        if not sample_data:
            sample_data = {
                "severity": "WARNING",
                "rule_name": "Sample Rule",
                "message": "This is a sample alert message",
                "status": "ACTIVE",
                "created_at": datetime.now(),
                "value": 95.5,
                "threshold": 90.0,
                "condition": ">",
                "trend": "↑ Increasing",
                "related_alerts": [
                    {
                        "created_at": datetime.now(),
                        "message": "Previous related alert"
                    }
                ],
                "recommendations": [
                    "Check system resources",
                    "Review recent changes"
                ]
            }
        
        return self.render_template(name, sample_data)
