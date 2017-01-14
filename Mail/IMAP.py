"""MailBox class for processing IMAP email.

(To use with Gmail: enable IMAP access in your Google account settings)

usage with GMail:

    import mailbox

    with mailbox.MailBox(gmail_username, gmail_password) as mbox:
        print mbox.get_count()
        print mbox.print_msgs()


for other IMAP servers, adjust settings as necessary.    
"""


import imaplib
import time
import uuid
import email
import pprint

IMAP_SERVER = 'imap.one.com'
IMAP_PORT = '993'
IMAP_USE_SSL = True



class IMAP(object):
    
    def __init__(self, user, password):
        self.user = user
        self.password = password
        if IMAP_USE_SSL:
            self.imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        else:
            self.imap = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)

    def __enter__(self):
        self.imap.login(self.user, self.password)
        return self

    def __exit__(self, type, value, traceback):
        self.imap.close()
        self.imap.logout()

    def get_count(self):
        #self.imap.login(self.user, self.password)
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'ALL')
        return sum(1 for num in data[0].split())

    def fetch_message(self, num):
        self.imap.select('Inbox')
        status, data = self.imap.fetch(str(num), '(RFC822)')
        email_msg = email.message_from_string(data[0][1])
        return email_msg

    def fetch_message_headers(self, num):
        ''' fetch flags and email headers from the mail specified by uid
        '''
        #self.imap.select('Inbox.Archives.2016')
        self.imap.select('Inbox')
        status, data = self.imap.uid('fetch',str(num), '(FLAGS BODY.PEEK[HEADER.FIELDS (DATE FROM TO SUBJECT)])')
        #print data[0][0]
        msg_headers = email.message_from_string( data[0][1].decode())
        return data[0][0], msg_headers

    def delete_message(self, num):
        self.imap.select('Inbox')
        self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()

    def delete_all(self):
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'ALL')
        for num in data[0].split():
            self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()

    def print_msgs(self):
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'ALL')
        for num in reversed(data[0].split()):
            status, data = self.imap.fetch(num, '(RFC822)')
            print ('Message %s\n%s\n' % (num, data[0][1]))

    def get_msg_uids(self):
        self.imap.select('Inbox')
        status, self.uids = self.imap.uid('search', None, "ALL")
        return self.uids

    def get_msg_uids_for_list_nw(self):
        self.imap.select('Inbox.Archives.2016')
        status, self.uids = self.imap.uid('search', None, '(SUBJECT "[Network]")')
        return self.uids

    def get_unseen_msg_uids(self):
        self.imap.select('Inbox')
        status, self.uids = self.imap.uid('search', None, "(UNSEEN)")
        return self.uids

    def print_msg_uids(self):
        self.imap.select('Inbox')
        status, data = self.imap.uid('search', None, "ALL")
        for num in reversed(data[0].split()):
            print ('%s ' % (num))

    def print_msg_summaries(self):
        self.imap.select('Inbox')
        status, data = self.imap.uid('search', None, "ALL")
        count = 0;
        for num in reversed(data[0].split()):
            count += 1
            if (count > 3):
                return
            data, headers = self.fetch_message_headers(num.decode('ascii'))
            pprint.pprint (data)
            #pprint.pprint (headers)
            print (num.decode('ascii')+" : "+headers['from']+" : "+headers['to']+" : "+headers['subject'])

    def get_latest_email_sent_to(self, email_address, timeout=300, poll=1):
        start_time = time.time()
        while ((time.time() - start_time) < timeout):
            # It's no use continuing until we've successfully selected
            # the inbox. And if we don't select it on each iteration
            # before searching, we get intermittent failures.
            status, data = self.imap.select('Inbox')
            if status != 'OK':
                time.sleep(poll)
                continue
            status, data = self.imap.search(None, 'TO', email_address)
            data = [d for d in data if d is not None]
            if status == 'OK' and data:
                for num in reversed(data[0].split()):
                    status, data = self.imap.fetch(num, '(RFC822)')
                    email_msg = email.message_from_string(data[0][1])
                    return email_msg
            time.sleep(poll)
        raise AssertionError("No email sent to '%s' found in inbox "
             "after polling for %s seconds." % (email_address, timeout))

    def delete_msgs_sent_to(self, email_address):
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'TO', email_address)
        if status == 'OK':
            for num in reversed(data[0].split()):
                status, data = self.imap.fetch(num, '(RFC822)')
                self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()



if __name__ == '__main__':
    # example:
    imap_username = ''
    imap_password = ''
    with IMAP(imap_username, imap_password) as mbox:
        print (mbox.get_count())
        #print mbox.print_msgs()
        mbox.print_msg_summaries()

