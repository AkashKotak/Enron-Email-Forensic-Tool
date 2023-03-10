import sys
import mailbox
from email.utils import getaddresses
from collections import defaultdict





def extract_sender(msg):
    """Extracts the sender's email address from the email message."""
    return getaddresses([msg['From']])[0][1]


def extract_recipients(msg):
    """Extracts the recipients' email addresses from the email message."""
    to_field = msg['To']
    cc_field = msg['Cc'] if msg['Cc'] else ''
    bcc_field = msg['Bcc'] if msg['Bcc'] else ''
    
    to_addrs = getaddresses(to_field.split(',')) if to_field else []
    cc_addrs = getaddresses(cc_field.split(',')) if cc_field else []
    bcc_addrs = getaddresses(bcc_field.split(',')) if bcc_field else []
    
    return [addr for _, addr in to_addrs + cc_addrs + bcc_addrs]


def extract_date(msg):
    """Extracts the date the email was sent from the email message."""
    return msg['Date']


def extract_body(msg):
    """Extracts the body of the email message."""
    payload = msg.get_payload()
    if isinstance(payload, str):
        return payload
    else:
        return '\n'.join([part.get_payload() for part in payload])


def search(term_set, mbox):
    """Searches for emails that contain all the terms in term_set."""
    results = []
    for i, msg in enumerate(mbox):
        body = extract_body(msg)
        if all(term.lower() in body.lower() for term in term_set):
            sender = extract_sender(msg)
            date = extract_date(msg)
            results.append((i+1, sender, date))
    return results


def address_search(first_name, last_name, mbox):
    """Searches for emails sent or received by a person with the given first and last name."""
    results = defaultdict(list)
    for msg in mbox:
        recipients = extract_recipients(msg)
        sender = extract_sender(msg)
        full_name = msg['From'].split()[0]
        if first_name.lower() in full_name.lower() and last_name.lower() in full_name.lower():
            results['Sent'].append(sender)
        for recipient in recipients:
            full_name = recipient.split()[0]
            if first_name.lower() in full_name.lower() and last_name.lower() in full_name.lower():
                results['Received'].append(recipient)
    return results


def interaction_search(addr1, addr2, mbox):
    """Searches for emails exchanged between two people."""
    results = []
    for i, msg in enumerate(mbox):
        sender = extract_sender(msg)
        recipients = extract_recipients(msg)
        if (addr1 in sender or addr1 in recipients) and (addr2 in sender or addr2 in recipients):
            results.append((i+1, sender, recipients, extract_date(msg)))
    return results


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: enron_search <command> <arguments>")
        sys.exit(1)

    

    command = sys.argv[1]
    mbox_filename = "C:\\Users\\Owner\\Desktop\\Assignment\\enron\\enron.allen-p.all_documents"
    mbox = mailbox.mbox(mbox_filename)

    
    if command == 'term_search':
        term_set = set(sys.argv[2:])
        
        results = search(term_set, mbox)
        for result in results:
           print("Message #{} - From: {}, Date: {}".format(result[0], result[1], result[2]))

    elif command == 'address_search':
        if len(sys.argv) != 4:
            print("Usage: enron_search address_search <first_name> <last_name>")
            sys.exit(1)
        first_name = sys.argv[2]
        last_name = sys.argv[3]
        results = address_search(first_name, last_name, mbox)
        print("Sent by {} {}:".format(first_name, last_name))
        for sender in results['Sent']:
            print(sender)
        print("Received by {} {}:".format(first_name, last_name))
        for recipient in results['Received']:
            print(recipient)

    elif command == 'interaction_search':
        if len(sys.argv) != 4:
            print("Usage: enron_search interaction_search <address_1> <address_2>")
            sys.exit(1)
        addr1 = sys.argv[2]
        addr2 = sys.argv[3]
        results = interaction_search(addr1, addr2, mbox)
        for result in results:
            print("Message #{} - From: {}, To: {}, Date: {}".format(result[0], result[1], result[2], result[3]))

    else:
        print("Invalid command.")
        sys.exit(1)