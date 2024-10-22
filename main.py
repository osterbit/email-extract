import mailbox
import email
import os
from jinja2 import Environment, FileSystemLoader
import pdfkit
from collections import defaultdict
import asyncio
from tqdm import tqdm
import json

# email_addressees = ['maryomoerlins@gmail.com']
email_addresses = [
"jsu5625j@gmail.com",
"margaret@hgsengineeringinc.com",
"summersm@uab.edu",
]

# Specify the path to your MBOX file
MBOX_FILE = 'data/All Mail including Spam and Trash.mbox'

# Specify the output directory for PDFs
OUTPUT_DIR = 'emails_to_print'

CHECKPOINT_FILE = 'checkpoint.json'
OUTPUT_FILE = 'target_emails.jsonl'

# to contain email addresses and the number of emails sent to each
address_count_tracker = defaultdict(int)

# to contain the count of processed emails 'target' and 'other'
processed_email_tracker = defaultdict(int)
target_emails = []

async def get_body(message):
    body = ''
    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip attachments
            if cdispo and 'attachment' in cdispo:
                continue
            if ctype == 'text/plain':
                return part.get_payload(decode=True).decode('utf-8', errors='ignore')
    else:
        return message.get_payload(decode=True).decode('utf-8', errors='ignore')
    # shouldn't get here...
    return body

async def process_email(idx, message, email_addresses, output_file):
    if message['from'] is None or message['to'] is None:
        return None
    from_address = email.utils.parseaddr(message['from'])[1]
    to_addresses = [email.utils.parseaddr(addr)[1] for addr in message['to'].split(',')]

    if (from_address in email_addresses) or any(addr in email_addresses for addr in to_addresses):
        subject = message.get('subject', '(No Subject)')
        date = message.get('date', '(No Date)')
        body = await get_body(message)
        email_data = {
            'from': from_address,
            'to': to_addresses,
            'subject': subject,
            'date': date,
            'body': body
        }
        output_file.write(json.dumps(email_data) + '\n')
    return idx

async def extract_emails(start_idx=0, email_addresses=email_addresses):
    mbox = mailbox.mbox(MBOX_FILE)
    total_emails = len(mbox)
    print(f"Total emails in mbox: {total_emails}")
    print(f"Starting email extraction from index {start_idx}")

    with open(OUTPUT_FILE, 'a') as output_file:
        tasks = []
        for idx in tqdm(range(start_idx, total_emails), initial=start_idx, total=total_emails):
            message = mbox.get_message(idx)
            task = asyncio.create_task(process_email(idx, message, email_addresses, output_file))
            tasks.append(task)

            # Limit the number of concurrent tasks
            if len(tasks) >= 100:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks = list(pending)

                # Save checkpoint
                for task in done:
                    if task.result() is not None:
                        with open(CHECKPOINT_FILE, 'w') as checkpoint_file:
                            json.dump({'last_processed_idx': task.result()}, checkpoint_file)

        # Wait for remaining tasks to complete
        if tasks:
            done, _ = await asyncio.wait(tasks)
            for task in done:
                if task.result() is not None:
                    with open(CHECKPOINT_FILE, 'w') as checkpoint_file:
                        json.dump({'last_processed_idx': task.result()}, checkpoint_file)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as checkpoint_file:
            checkpoint_data = json.load(checkpoint_file)
            return checkpoint_data.get('last_processed_idx', 0)
    return 0

def main():
    start_idx = load_checkpoint()
    if start_idx > 0:
        print(f"Resuming from email index {start_idx}")
    else:
        print("Starting email extraction from the beginning")
    asyncio.run(extract_emails(start_idx))
    print("Email extraction completed")

if __name__ == "__main__":
    main()
