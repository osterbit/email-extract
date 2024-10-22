import sys
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

def load_data_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def load_data_from_stdin():
    return [json.loads(line) for line in sys.stdin]

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        data = load_data_from_file(file_path)
    else:
        data = load_data_from_stdin()

    template_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email List Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                background-color: #f5f5f5;
                padding: 20px;
            }
            .email {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 8px;
                margin: 20px 0;
                padding: 15px;
            }
            .email-header {
                font-weight: bold;
            }
            .email-body {
                white-space: pre-wrap;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        {% for email in emails %}
        <div class="email">
            <div class="email-header">From: {{ email.from }}</div>
            <div class="email-header">To: {{ email.to | join(', ') }}</div>
            <div class="email-header">Subject: {{ email.subject }}</div>
            <div class="email-header">Date: {{ email.date }}</div>
            <div class="email-body">{{ email.body }}</div>
        </div>
        {% endfor %}
    </body>
    </html>
    """

    # Create a Jinja environment and compile the template
    env = Environment(
        loader=FileSystemLoader(searchpath="."),
        autoescape=select_autoescape(['html', 'xml'])
    )

    # Load the template from the inline HTML
    template = env.from_string(template_html)

    # Render the template with the provided data
    output_html = template.render(emails=data)

    # Write the rendered HTML to a file
    output_file = "email_list_report.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_html)

    print(f"HTML file generated successfully: {output_file}")

if __name__ == "__main__":
    main()