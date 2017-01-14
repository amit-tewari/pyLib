import pprint
import email

class NetworkList(object):
    def __init__(self):
        self.mail_type=""
        self.system=""
        self.action_or_status=""

    def __enter__(self):
        return self

    def __exit__(self, type, value, tracebask):
        pass

    def classify(self, uid, headers):
        sender = headers['from']
        recipient = headers['to']
        subject = headers['subject']
        #pprint.pprint (uid + " : " + sender + " : " + recipient  + " : " + subject)
        #subject = subject.replace("A", ' A')
        subject_tokens = subject.split()
        #if subject_tokens[0]=='[Network]':
            #print map(subject_tokens.__getitem__, (0, 1, 2, 3, 4, 5))
        #print (str(len(subject_tokens)) + " : " + " ".join(subject_tokens))
        if (len(subject_tokens) == 6):
            if (subject_tokens[1]== "unattended-upgrades"):
                self.mail_type = "unattended-upgrades"
                self.system    = subject_tokens[4]
                if subject_tokens[5] == "'True'":
                    self.action_or_status = 'package Update Needed'
        elif (len(subject_tokens) == 7):
            if (subject_tokens[1]== "ALERT:") and (subject_tokens[4]== "[Red") and (subject_tokens[5]== "Alarm]"):
                self.mail_type = "Red Alarm"
                self.system    = subject_tokens[2]
                self.action_or_status = subject_tokens[6]
            elif (subject_tokens[1]== "[syslog]") and (subject_tokens[3]== "RPD_BGP_NEIGHBOR_STATE_CHANGED"):
                self.mail_type = "RPD_BGP_NEIGHBOR_STATE_CHANGED"
                self.system    = subject_tokens[2]
                self.action_or_status = "change"
            elif (subject_tokens[1]== "Hibernia") and (subject_tokens[4]== "Notification"):
                self.mail_type = "Hibernia Notification"
                self.system    = "Network"
                self.action_or_status = "notice"
                #print "RED ALARM"
        return self.mail_type, self.system, self.action_or_status

