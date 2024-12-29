import os
import csv
import re
import html

def sanitize_input(input_text):
    """Sanitize user input to prevent XSS and SQL injection attacks."""
    sanitized_text = html.escape(input_text)  # Escape HTML characters
    sanitized_text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', sanitized_text)  # Remove control characters
    sanitized_text = re.sub(r'(--|;|\'|"|\\|\/|\*|=|<|>)', '', sanitized_text)  # Remove SQL injection patterns
    sanitized_text = re.sub(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|RENAME|TRUNCATE|EXEC)\b', '', sanitized_text, flags=re.IGNORECASE)
    return sanitized_text

def save_feedback(name, feedback, rating):
    """Save feedback to a CSV file."""
    feedback_file = "local_feedback/feedback.csv"
    if not os.path.exists("local_feedback"):
        os.makedirs("local_feedback")

    file_exists = os.path.exists(feedback_file)

    with open(feedback_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:  # Write header if file is new
            writer.writerow(["Name", "Feedback", "Rating"])
        writer.writerow([name, feedback, rating])