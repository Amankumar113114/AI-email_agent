import imaplib
import email
from email.header import decode_header
from transformers import pipeline
import re
from flask import Flask, request, render_template_string

# Initialize AI models (pre-trained; download on first run)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
classifier = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment")  # Adapt for email categories
generator = pipeline("text-generation", model="gpt2")

# Flask app for UI
app = Flask(__name__)

# Function to connect to email server
def connect_email(server, username, password):
    mail = imaplib.IMAP4_SSL(server)
    mail.login(username, password)
    mail.select("inbox")
    return mail

# Function to fetch recent emails (simplified to one thread)
def fetch_emails(mail, num_emails=10):
    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split()[-num_emails:]  # Last N emails
    emails = []
    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        subject = decode_header(msg["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
        emails.append({"subject": subject, "body": body})
    return emails

# Function to compress thread (summarize)
def compress_thread(emails):
    full_text = " ".join([e["body"] for e in emails])
    if len(full_text) > 1000:  # Summarize if long
        summary = summarizer(full_text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
    else:
        summary = full_text
    return summary

# Function to categorize email
def categorize_email(body):
    # Simple rule-based + AI: Map sentiment to categories (adapt model for better classification)
    result = classifier(body)[0]
    label = result['label']
    if label == 'LABEL_2':  # Positive, assume personal
        return "Personal"
    elif label == 'LABEL_0':  # Negative, assume urgent
        return "Urgent"
    else:
        return "Work-Related"  # Neutral

# Function to generate response
def generate_response(context, category):
    prompt = f"Write a professional response to this {category} email: {context[:500]}"  # Limit prompt
    response = generator(prompt, max_length=100, num_return_sequences=1, do_sample=True)[0]['generated_text']
    # Clean up response (remove prompt echo)
    response = re.sub(r".*email:\s*", "", response, flags=re.IGNORECASE).strip()
    return response

# Mock data for testing (uncomment to use instead of real email)
# def mock_fetch_emails():
#     return [
#         {"subject": "Meeting Reminder", "body": "Don't forget our meeting tomorrow at 10 AM."},
#         {"subject": "Re: Meeting Reminder", "body": "Got it, see you then."}
#     ]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        server = request.form['server']
        username = request.form['username']
        password = request.form['password']
        try:
            mail = connect_email(server, username, password)
            emails = fetch_emails(mail, 5)  # Fetch last 5
            # emails = mock_fetch_emails()  # Uncomment for mock
            if emails:
                summary = compress_thread(emails)
                category = categorize_email(emails[-1]["body"])  # Categorize latest
                suggested_response = generate_response(summary, category)
                mail.logout()
                return render_template_string("""
                <h1>Email Agent Results</h1>
                <p><strong>Thread Summary:</strong> {{ summary }}</p>
                <p><strong>Category:</strong> {{ category }}</p>
                <p><strong>Suggested Response:</strong> {{ response }}</p>
                <a href="/">Back</a>
                """, summary=summary, category=category, response=suggested_response)
            else:
                return "No emails found."
        except Exception as e:
            return f"Error: {str(e)}"
    return render_template_string("""
    <h1>Email Management Agent</h1>
    <form method="post">
        Server: <input name="server" value="imap.gmail.com"><br>
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <input type="submit" value="Process Emails">
    </form>
    """)

if __name__ == '__main__':
    app.run(debug=True)