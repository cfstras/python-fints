import glob
import os.path
import pytest
import http.server
import threading
import base64
import uuid
import re

import fints.parser
from fints.types import SegmentSequence
from fints.segments.message import HNHBK3, HNVSK3, HNVSD1, HNHBS1
from fints.formals import SecurityProfile, SecurityIdentificationDetails, SecurityDateTime, EncryptionAlgorithm, KeyName, BankIdentifier

TEST_MESSAGES = {
    os.path.basename(f).rsplit('.')[0]: open(f, 'rb').read() for f in 
    glob.glob(os.path.join(os.path.dirname(__file__), "messages", "*.bin"))
}

# We will turn off robust mode generally for tests
fints.parser.robust_mode = False

@pytest.fixture(scope="session")
def fints_server():
    dialog_prefix = base64.b64encode( uuid.uuid4().bytes, altchars=b'_/' ).decode('us-ascii')
    system_prefix = base64.b64encode( uuid.uuid4().bytes, altchars=b'_/' ).decode('us-ascii')
    dialogs = {}
    systems = {}

    class FinTSHandler(http.server.BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def make_answer(self, dialog_id, message):
            datadict = dialogs[dialog_id]

            result = []

            result.append(b"HIRMG::2+0010::Nachricht entgegengenommen'")

            if b"'HKVVB:" in message:
                result.append(b"HIRMS::2:4+3050::BPD nicht mehr aktuell, aktuelle Version enthalten.+3050::UPD nicht mehr aktuell, aktuelle Version enthalten.+3920::Zugelassene TAN-Verfahren fur den Benutzer:942+0901::*PIN gultig.+0020::*Dialoginitialisierung erfolgreich'HIRMS:5:2:5+0020::Auftrag ausgefuhrt.'HIBPA:6:3:4+78+280:12345678+FinTSJSClient Test Bank+1+1+300+500'HIKOM:7:4:4+280:12345678+1+3:http?://localhost?:3000/cgi-bin/hbciservlet+2:localhost?:3000'HISHV:8:3:4+J+RDH:3+PIN:1+RDH:9+RDH:10+RDH:7'HIEKAS:9:5:4+1+1+1+J:J:N:3'HIKAZS:10:4:4+1+1+365:J'HIKAZS:11:5:4+1+1+365:J:N'HIKAZS:12:6:4+1+1+1+365:J:N'HIKAZS:13:7:4+1+1+1+365:J:N'HIPPDS:14:1:4+1+1+1+1:Telekom:prepaid:N:::15;30;50:2:Vodafone:prepaid:N:::15;25;50:3:E-Plus:prepaid:N:::15;20;30:4:O2:prepaid:N:::15;20;30:5:Congstar:prepaid:N:::15;30;50:6:Blau:prepaid:N:::15;20;30'HIPAES:15:1:4+1+1+1'HIPROS:16:3:4+1+1'HIPSPS:17:1:4+1+1+1'HIQTGS:18:1:4+1+1+1'HISALS:19:5:4+3+1'HISALS:20:7:4+1+1+1'HISLAS:21:4:4+1+1+500:14:04:05'HICSBS:22:1:4+1+1+1+N:N'HICSLS:23:1:4+1+1+1+J'HICSES:24:1:4+1+1+1+1:400'HISUBS:25:4:4+1+1+500:14:51:53:54:56:67:68:69'HITUAS:26:2:4+1+1+1:400:14:51:53:54:56:67:68:69'HITUBS:27:1:4+1+1+J'HITUES:28:2:4+1+1+1:400:14:51:53:54:56:67:68:69'HITULS:29:1:4+1+1'HICCSS:30:1:4+1+1+1'HISPAS:31:1:4+1+1+1+J:J:N:sepade?:xsd?:pain.001.001.02.xsd:sepade?:xsd?:pain.001.002.02.xsd:sepade?:xsd?:pain.001.002.03.xsd:sepade?:xsd?:pain.001.003.03.xsd:sepade?:xsd?:pain.008.002.02.xsd:sepade?:xsd?:pain.008.003.02.xsd'HICCMS:32:1:4+1+1+1+500:N:N'HIDSES:33:1:4+1+1+1+3:45:6:45'HIBSES:34:1:4+1+1+1+2:45:2:45'HIDMES:35:1:4+1+1+1+3:45:6:45:500:N:N'HIBMES:36:1:4+1+1+1+2:45:2:45:500:N:N'HIUEBS:37:3:4+1+1+14:51:53:54:56:67:68:69'HIUMBS:38:1:4+1+1+14:51'HICDBS:39:1:4+1+1+1+N'HICDLS:40:1:4+1+1+1+0:0:N:J'HIPPDS:41:2:4+1+1+1+1:Telekom:prepaid:N:::15;30;50:2:Vodafone:prepaid:N:::15;25;50:3:E-plus:prepaid:N:::15;20;30:4:O2:prepaid:N:::15;20;30:5:Congstar:prepaid:N:::15;30;50:6:Blau:prepaid:N:::15;20;30'HICDNS:42:1:4+1+1+1+0:1:3650:J:J:J:J:N:J:J:J:J:0000:0000'HIDSBS:43:1:4+1+1+1+N:N:9999'HICUBS:44:1:4+1+1+1+N'HICUMS:45:1:4+1+1+1+OTHR'HICDES:46:1:4+1+1+1+4:1:3650:000:0000'HIDSWS:47:1:4+1+1+1+J'HIDMCS:48:1:4+1+1+1+500:N:N:2:45:2:45::sepade?:xsd?:pain.008.003.02.xsd'HIDSCS:49:1:4+1+1+1+2:45:2:45::sepade?:xsd?:pain.008.003.02.xsd'HIECAS:50:1:4+1+1+1+J:N:N:urn?:iso?:std?:iso?:20022?:tech?:xsd?:camt.053.001.02'GIVPUS:51:1:4+1+1+1+N'GIVPDS:52:1:4+1+1+1+1'HITANS:53:5:4+1+1+1+J:N:0:942:2:MTAN2:mobileTAN::mobile TAN:6:1:SMS:3:1:J:1:0:N:0:2:N:J:00:1:1:962:2:HHD1.4:HHD:1.4:Smart-TAN plus manuell:6:1:Challenge:3:1:J:1:0:N:0:2:N:J:00:1:1:972:2:HHD1.4OPT:HHDOPT1:1.4:Smart-TAN plus optisch:6:1:Challenge:3:1:J:1:0:N:0:2:N:J:00:1:1'HIPINS:54:1:4+1+1+1+5:20:6:Benutzer ID::HKSPA:N:HKKAZ:N:HKKAZ:N:HKSAL:N:HKSLA:J:HKSUB:J:HKTUA:J:HKTUB:N:HKTUE:J:HKTUL:J:HKUEB:J:HKUMB:J:HKPRO:N:HKEKA:N:HKKAZ:N:HKKAZ:N:HKPPD:J:HKPAE:J:HKPSP:N:HKQTG:N:HKSAL:N:HKCSB:N:HKCSL:J:HKCSE:J:HKCCS:J:HKCCM:J:HKDSE:J:HKBSE:J:HKDME:J:HKBME:J:HKCDB:N:HKCDL:J:HKPPD:J:HKCDN:J:HKDSB:N:HKCUB:N:HKCUM:J:HKCDE:J:HKDSW:J:HKDMC:J:HKDSC:J:HKECA:N:GKVPU:N:GKVPD:N:HKTAN:N:HKTAN:N'HIAZSS:55:1:4+1+1+1+1:N:::::::::::HKTUA;2;0;1;811:HKDSC;1;0;1;811:HKPPD;2;0;1;811:HKDSE;1;0;1;811:HKSLA;4;0;1;811:HKTUE;2;0;1;811:HKSUB;4;0;1;811:HKCDL;1;0;1;811:HKCDB;1;0;1;811:HKKAZ;6;0;1;811:HKCSE;1;0;1;811:HKSAL;4;0;1;811:HKQTG;1;0;1;811:GKVPU;1;0;1;811:HKUMB;1;0;1;811:HKECA;1;0;1;811:HKDMC;1;0;1;811:HKDME;1;0;1;811:HKSAL;7;0;1;811:HKSPA;1;0;1;811:HKEKA;5;0;1;811:HKKAZ;4;0;1;811:HKPSP;1;0;1;811:HKKAZ;5;0;1;811:HKCSL;1;0;1;811:HKCDN;1;0;1;811:HKTUL;1;0;1;811:HKPPD;1;0;1;811:HKPAE;1;0;1;811:HKCCM;1;0;1;811:HKIDN;2;0;1;811:HKDSW;1;0;1;811:HKCUM;1;0;1;811:HKPRO;3;0;1;811:GKVPD;1;0;1;811:HKCDE;1;0;1;811:HKBSE;1;0;1;811:HKCSB;1;0;1;811:HKCCS;1;0;1;811:HKDSB;1;0;1;811:HKBME;1;0;1;811:HKCUB;1;0;1;811:HKUEB;3;0;1;811:HKTUB;1;0;1;811:HKKAZ;7;0;1;811'HIVISS:56:1:4+1+1+1+1;;;;'HIUPA:57:4:4+test1+3+0'HIUPD:58:6:4+1::280:12345678+DE111234567800000001+test1++EUR+Fullname++Girokonto++HKSAK:1+HKISA:1+HKSSP:1+HKSAL:1+HKKAZ:1+HKEKA:1+HKCDB:1+HKPSP:1+HKCSL:1+HKCDL:1+HKPAE:1+HKPPD:1+HKCDN:1+HKCSB:1+HKCUB:1+HKQTG:1+HKSPA:1+HKDSB:1+HKCCM:1+HKCUM:1+HKCCS:1+HKCDE:1+HKCSE:1+HKDSW:1+HKPRO:1+HKSAL:1+HKKAZ:1+HKTUL:1+HKTUB:1+HKPRO:1+GKVPU:1+GKVPD:1'HIUPD:59:6:4+2::280:12345678+DE111234567800000002+test1++EUR+Fullname++Tagesgeld++HKSAK:1+HKISA:1+HKSSP:1+HKSAL:1+HKKAZ:1+HKEKA:1+HKPSP:1+HKCSL:1+HKPAE:1+HKCSB:1+HKCUB:1+HKQTG:1+HKSPA:1+HKCUM:1+HKCCS:1+HKCSE:1+HKPRO:1+HKSAL:1+HKKAZ:1+HKTUL:1+HKTUB:1+HKPRO:1+GKVPU:1+GKVPD:1'")

            if b"'HKSYN:" in message:
                system_id = "{};{:05d}".format(system_prefix, len(systems)+1)
                systems[system_id] = {}
                result.append("HISYN::4:5+{}'".format(system_id).encode('us-ascii'))

            if b"'HKSPA:" in message:
                result.append(b"HISPA::1:4+J:DE111234567800000001:GENODE00TES:00001::280:1234567890'")

            return b"".join(result)


        def process_message(self, message):
            incoming_dialog_id = re.match(rb'HNHBK:1:3\+\d+\+300\+([^+]+)', message)

            if incoming_dialog_id:
                dialog_id = incoming_dialog_id.group(1).decode('us-ascii')
                if dialog_id == '0':
                    dialog_id = "{};{:05d}".format(dialog_prefix, len(dialogs)+1)
                    dialogs[dialog_id] = {'in_messages': []}

                datadict = dialogs[dialog_id]
                datadict['in_messages'].append(message)

                answer = self.make_answer(dialog_id, message)

                retval = SegmentSequence([
                    HNHBK3(hbci_version=300, dialogue_id=dialog_id, message_number=len(datadict['in_messages'])),
                    HNVSK3(
                        SecurityProfile('PIN', '1'),
                        '998',
                        '1',
                        SecurityIdentificationDetails('1', None, '0'),
                        SecurityDateTime('1'),
                        EncryptionAlgorithm('2', '2', '13', None, '5', '1'),
                        KeyName(BankIdentifier('280', '1234567890'), '0', 'S', 0, 0),
                        '0',
                    ),
                    HNVSD1(),
                    HNHBS1(message_number=len(datadict['in_messages'])),
                ])
                retval.segments[2].data = answer

                for i, seg in enumerate(retval.find_segments(callback=lambda s: s.header.type not in ('HNVSK', 'HNVSD'))):
                    seg.header.number = i

                return retval.render_bytes()

            return b""

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            message = base64.b64decode(post_data)

            response = self.process_message(message)

            content_data = base64.b64encode(response)
            self.send_response(200)
            self.send_header('Content-Length', len(content_data))
            self.end_headers()
            self.wfile.write(content_data)


    server = http.server.HTTPServer(('127.0.0.1', 0), FinTSHandler)
    thread = threading.Thread(target=server.serve_forever, name="fints_server", daemon=True)
    thread.start()

    yield "http://{0}:{1}/".format(*server.server_address)

    server.shutdown()
    thread.join()
