# Alert and Notification Templates

## Alert Templates

Alert templates define how monitoring alerts are formatted and handled.

### Default Templates

```json
{
    "cpu_high": {
        "title": "High CPU Usage",
        "message": "CPU usage is at {value}% (threshold: {threshold}%)",
        "level": "warning",
        "threshold": 80,
        "duration": 300,
        "actions": ["notify", "log"]
    }
}
```

### Custom Templates

Create `~/.config/process-dashboard/alert_templates.json`:

```json
{
    "custom_alert": {
        "title": "Custom Alert",
        "message": "Custom message: {value}",
        "level": "info",
        "threshold": 50,
        "duration": 0,
        "actions": ["log"]
    }
}
```

## Notification Templates

Templates for different notification types.

### Email Templates

```json
{
    "alert": {
        "subject": "Process Dashboard Alert: {level}",
        "body": "Alert message content..."
    }
}
```

### Desktop Templates

```json
{
    "alert": {
        "title": "Process Dashboard {level}",
        "body": "{message}",
        "urgency": "critical"
    }
}
```

### Log Templates

```json
{
    "alert": "[{timestamp}] [{level}] {title}: {message}",
    "metric": "[{timestamp}] METRIC {name}={value} {unit}"
}
```

## Usage

### Using Templates

```python
from monitoring.templates.alert_templates import AlertTemplate
from monitoring.templates.notification_templates import NotificationFormatter

# Create alert
alert_template = AlertTemplate()
alert = alert_template.format_alert("cpu_high", {
    "value": 85,
    "threshold": 80
})

# Format notification
formatter = NotificationFormatter()
email = formatter.format_email("alert", {
    "level": "warning",
    "title": "High CPU",
    "message": alert
})
```

### Custom Templates

1. Create template file:
```json
{
    "email": {
        "custom_report": {
            "subject": "Custom Report: {title}",
            "body": "Report content: {content}"
        }
    }
}
```

2. Use custom template:
```python
formatter = NotificationFormatter()
message = formatter.format_email("custom_report", {
    "title": "Daily Summary",
    "content": "Report details..."
})
```

## Template Variables

### Alert Templates
- `{value}`: Current value
- `{threshold}`: Alert threshold
- `{timestamp}`: Current time
- `{level}`: Alert level

### Notification Templates
- `{title}`: Alert title
- `{message}`: Alert message
- `{timestamp}`: Current time
- `{level}`: Notification level

## Best Practices

1. Keep templates simple
2. Use consistent formatting
3. Include relevant context
4. Test templates
5. Document custom templates

