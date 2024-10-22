from tqdm import tqdm


def search_mbox_line_by_line(mbox_path, search_addresses):
    with open(mbox_path, 'r', encoding='utf-8', errors='replace') as f:
        message_lines = []
        in_message = False
        for line in tqdm(f):
            if line.startswith('From '):
                if message_lines:
                    if is_relevant_message(message_lines, search_addresses):
                        process_message(message_lines)
                    message_lines = []
                in_message = True
            if in_message:
                message_lines.append(line)
        # Process the last message
        if message_lines and is_relevant_message(message_lines, search_addresses):
            process_message(message_lines)

def is_relevant_message(lines, search_addresses):
    headers = ''.join(lines[:50])  # Assuming headers are within the first 50 lines
    for address in search_addresses:
        if address.lower() in headers.lower():
            return True
    return False

def process_message(lines):
    # Write the message to an output file or process as needed
    with open('data/filtered_emails.mbox', 'a', encoding='utf-8') as f_out:
        f_out.writelines(lines)


def main():
    email_addressees = ['maryomoerlins@gmail.com']
    # email_addresses = ["mpaurin@uchicago.edu"]

    # Specify the path to your MBOX file
    MBOX_FILE = 'data/All Mail including Spam and Trash.mbox'
    search_mbox_line_by_line(MBOX_FILE, email_addressees)



if __name__ == '__main__':
    main()
