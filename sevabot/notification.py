# -*- coding: utf-8 -*-
from trac.core import *
from trac.ticket.model import Ticket
from trac.ticket.api import ITicketChangeListener
from trac.config import *
from trac.util.text import obfuscate_email_address

import urllib
import md5


class SevabotNotificationPlugin(Component):
    implements(ITicketChangeListener)

    host = Option('sevabot','host','localhost',"""
sevabot host
""")
    port = IntOption('sevabot','port','5000',"""
sevabot port
""")
    shared_secret = Option('sevabot','shared_secret','SHARED_KEY',"""
sevabot shared secret key
""")
    chat=Option('sevabot','chat','CHAT_ID',"""
Target skype chat room (Please get chat id from sevabot)
""")

    # ITicketChangeListener methods
    def ticket_created(self,ticket):
        self.env.log.debug('ticket created')
        self._post_hook('CREATED',ticket,ticket['reporter'])
        return

    def ticket_deleted(self,ticket):
        self.env.log.debug('ticket deleted')
        self._post_hook('DELETED',ticket,ticket['reporter'])
        return

    def ticket_changed(self,ticket, comment, author, old_values):
        self.env.log.debug('ticket changed')
        self._post_hook(ticket['status'],ticket,author)
        return

    def _post_hook(self,event,ticket,author):
        url = u"http://{host}:{port}/msg/".format(host=self.host,port=self.port)
        id = ticket.id
        summary = ticket['summary']
        link = self.env.abs_href.ticket(ticket.id)
        author = self.obfuscate_email(author)
        message = u"[{event}]({author}) {id}:{summary}\n{link}".format(event=event,author=author,id=id,summary=summary,link=link)
        key = self.chat+message+self.shared_secret
        m = md5.new(key.encode('utf-8')).hexdigest()
        params=urllib.urlencode({'chat':self.chat,'msg':message.encode('utf-8'),'md5':m})
	urllib.urlopen(url,params)

    def obfuscate_email(self, text):
        if self.env.config.getbool('trac', 'show_email_addresses'):
            return text
        else:
            return obfuscate_email_address(text)

