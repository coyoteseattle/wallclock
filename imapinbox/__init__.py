import time
import imaplib

class imapInbox:
    def __init__(self,server,username,password,logger):
        self.logger=logger
        self.server=server
        self.username=username
        self.password=password
        self.last_update=0
        self.last_data='<div class="email"><div class="mailcount">📨???</div><div class="mailsubjects"></div></div>'
        self.connect()

    def connect(self):
        try:
            self.connection=imaplib.IMAP4_SSL(host=self.server,timeout=30)
        except Exception as e:
            self.logger.exception('Failed to connect to IMAP server')
            raise e
        try:
            status,type = self.connection.login(self.username,self.password)
        except Exception as e:
            self.logger.error('Failed to log in to configured IMAP server. Check password?')
            raise e
        self.connection.enable('UTF8=ACCEPT')
        self.connection.select('INBOX',readonly=1)

    def return_old_data(self):
        if time.time() - self.last_update>600:
            self.last_data='<div class="mail"><div class="mail-count">📨???</div><div class="mail-subjects"><div class="mail-subject error">Error fetching mail data</div></div></div>'
            self.last_update=time.time()
        return self.last_data

    def get_head(self,message):
        try:
            status,data=self.connection.fetch(message,'(BODY[HEADER.FIELDS (SUBJECT)])')
        except:
            try:
                self.connect()
                status,data=self.connection.fetch(message,'(BODY[HEADER.FIELDS (SUBJECT)])')
            except Exception as e:
                raise e
        output = {}
        for line in data[0][1].splitlines():
            parsed=line.decode('UTF-8').split(': ')
            output[parsed[0].lower()]=': '.join(parsed[1:])
        output['id']=message
        return output

    def get_subjects(self,messages):
        output=[]
        for message in messages:
            try:
                head = self.get_head(message)
                if 'subject' in head:
                    output.append(head)
            except Exception as e:
                self.logger.exception('a')
        output.sort(key=lambda x:x['id'])
        print(output)
        return '<div class="mail-subjects">'+''.join([f'<div class="mail-subject">{x["subject"]}</div>' for x in output[-5:]])+'</div>'

    def get_data(self):
        try:
            status,data=self.connection.search(None,'(UNSEEN)')
        except:
            try:
                self.connect()
                status,data=self.connection.search(None,'(UNSEEN)')
            except:
                return self.return_old_data()
        mail_count=len(data[0].split())
        subject_block=self.get_subjects(data[0].split())
        self.last_output=f'<div class="mail"><div class="mail-count">📨 {mail_count}</div>{subject_block}</div>'
        self.last_updated=time.time()
        return self.last_output

