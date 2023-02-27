import re
from datetime import datetime

import Util
import Crypto_Util as Crypto
import Message
import Process
import Protocol

MODE_DSP = 220
MODE_CMU = 210
MODE_CA = 230

MODE_ELSE = 240

C2_WAIT_HANDSHAKE = 1001
C2_CMU_HELLO_SEND = 1002
C2_DSP_HELLO_RECEIVED = 1003
C2_DSP_CERT_SEND = 1004
C2_CMU_CERT_RECEIVED = 1005
C2_CMU_KEY_SEND = 1006
C2_DSP_KEY_RECEIVED = 1007
C2_DONE = 1008


class Entity:
    WAIT_START = 1000
    WORKING = 1001

    def __init__(self):
        self._hackrf_serial = None
        self._rtl_serial = None
        self._recv_signal = None
        self._trans_freq = 131.45
        self._addr = None
        self._hackrf_event = None
        self._rtl_event = None
        self._sym_key = None
        self._sym_key_c2 = None
        self._iv = None
        self._blk_signal = None
        self._com_signal = None
        self._test_signal = None
        self._not_signal = None
        self._c2_done_veri_signal = None 
        self._sec_level = 0
        self.entity_num = None
        self._cert_key = None
        self.work_space = "users/"
        self.statu = self.WAIT_START
        self.protocol = None
        self.custom2_statu = None

    def getHackRF(self):
        return self._hackrf_serial

    def setHackRFSerial(self, serial):
        self._hackrf_serial = serial

    def initHackRF(self):
        self.protocol.setSendingDevice(self._hackrf_serial, self._trans_freq)

    def initRtl(self):
        self.protocol.setReceivingDevice(
            self._rtl_serial, self._trans_freq, self._addr)
        self.protocol.startRtl()

    def getRtl(self):
        return self._rtl_serial

    def setRtl(self, serial):
        self._rtl_serial = serial

    def setFrequency(self, freq):
        if freq != '':
            self._trans_freq = float(freq)

    def getFrequency(self):
        return self._trans_freq

    def setHostAndPort(self, addr):
        self._addr = addr

    def getHostAndPort(self):
        return self._addr

    def genEntityNum(self):
        return self.entity_num

    def putSignals(self, blk_signal, com_signal, notification_signal, c2_done_verify_signal):
        self._blk_signal = blk_signal
        self._com_signal = com_signal
        self._not_signal = notification_signal
        self._c2_done_veri_signal = c2_done_verify_signal

    def putTestingSignal(self, signal):
        self._test_signal = signal

    def forceStopDevices(self):
        self.protocol.forceStopDevices()

    def setSelfKey(self, key):
        self._cert_key = key

    def setCert(self, paras):
        pass
        #self.ca.genClientCert(self.work_space, paras, self.entity_num, self._cert_key)
        #Crypto.Security.cert_test(self.work_space, paras, self.entity_num, self._cert_key)

    def setSecurityLevel(self, level):
        self._sec_level = level

    def getModeNum(self):
        return self.entity_num

    def getSign(self, cipher):
        pass

    def verifySign(self, cipher, sign):
        pass

    def changeStatu(self):
        self.statu = self.WORKING

    def getDSPCert(self):
        return Crypto.Security.getCert("/home/jiaxv/inoproject/Acars_Security/users/dsp/dspcert.pem")

    def setSymmetricKeyandIV(self, key, iv):
        self._sym_key = key
        self._iv = iv

    def symmetricEncrypt(self, plain_text):
        return Crypto.Security.symmetricEncrypt(self._sym_key, self._iv, plain_text)

    def symmetricDecrypt(self, cipher_text):
        return Crypto.Security.symmetricDecrypt(self._sym_key, self._iv, cipher_text)

    def getSymKey(self, cert):
        ret = Crypto.Security.verifyCert(cert)
        if ret == 0:
            self._not_signal.emit("Success", "Verify DSP Certificate Success!")
            return Crypto.Security.encryptSymKey(cert)
        else:
            self._not_signal.emit("Wrong", "Verify DSP Certificate Fail!")
            return (None, None)
        
    def clearItems(self):
        self.protocol.clearItems()

    #收到数据块
    #def receiveBlock(self, dict):
    #    if dict.get("statu") != 1000:
    #        self._not_signal.emit("Wrong", dict.get("errormsg"))
    #        return None
    #    try:
    #        timestamp = dict.get("timestamp")
    #        timestamp = datetime.fromtimestamp(
    #            timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
    #        ack = "" if dict.get("ack") == False else dict.get("ack")
    #        try:
    #            orient = MODE_DSP if re.compile(
    #                r"[A-Za-z]").match(dict.get("block_id")) else MODE_CMU
    #        except:
    #            orient = MODE_ELSE

    #        msg = Message.Message((timestamp, orient, self._sec_level, dict.get("mode"), dict.get("label"), dict.get("tail"),
    #                               dict.get("block_id"), ack,  dict.get("flight"), dict.get("text"), dict.get("msgno"), dict.get("crc")[:2], dict.get("end")))
    #    except Exception:
    #        msg = None

    #    return msg
    
    def interpreteBlock(self, dict):
        if dict.get("statu") != 1000:
            self._not_signal.emit("Wrong", dict.get("errormsg"))
            return None
        try:
            timestamp = dict.get("timestamp")
            timestamp = datetime.fromtimestamp(
                timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
            ack = "" if dict.get("ack") == False else dict.get("ack")
            try:
                orient = MODE_DSP if re.compile(
                    r"[A-Za-z]").match(dict.get("block_id")) else MODE_CMU
            except:
                orient = MODE_ELSE

            msg_tuple = (timestamp, orient, self._sec_level, dict.get("mode"), dict.get("label"), dict.get("tail"),
                                   dict.get("block_id"), ack,  dict.get("flight"), dict.get("text"), dict.get("msgno"), dict.get("crc")[:2], dict.get("end"))

        except Exception:
            msg_tuple = None

        return msg_tuple

    #处理由数个数据块组合成的完整数据报
    def receiveCompleteMsg(self, dict):
        msg_tuple = self.interpreteBlock(dict)
        if msg_tuple is None:
            return None

        origin_text = dict.get("text")

        processed_text = ""
        sign_text = ""
        sign_valide = Message.MSG_WITH_NO_SIGN
        cipher_text = ""
        if self._sec_level == Message.Message.NORMAL:
            processed_text = origin_text
        elif self._sec_level == Message.Message.CUSTOM:
            try:
                to_text = Process.messageDecode(origin_text)
                sign_len = to_text[0]
                curr_len = 1+sign_len
                sign_text = to_text[1:curr_len]
                cipher_text = to_text[curr_len:]

                sign_valide = self.verifySign(cipher_text, sign_text)
                processed_text = self.symmetricDecrypt(cipher_text)
            except:
                processed_text = origin_text
        elif self._sec_level == Message.Message.CUSTOM2:
            if self.entity_num == MODE_DSP:
                #收到“hello”
                if self.custom2_statu == C2_WAIT_HANDSHAKE:
                    self.custom2_statu = C2_DSP_HELLO_RECEIVED
                    processed_text = origin_text
                    self.putMessageParas(
                        [("2", "P8", self.getCurrentArn(), "A", "", "", self.getDSPCert(), "")])
                elif self.custom2_statu == C2_DSP_CERT_SEND:
                    processed_text = Process.messageDecode(origin_text)
                    sym_key = Crypto.Security.decryptSymKey(processed_text)
                    if sym_key is not None:
                        self._sym_key = sym_key.decode("latin1")
                        self.custom2_statu = C2_DONE
                        self._c2_done_veri_signal.emit()
                    else:
                        self.custom2_statu = C2_WAIT_HANDSHAKE
                elif self.custom2_statu == C2_DONE:
                    to_text = Process.messageDecode(origin_text)
                    processed_text = self.symmetricDecrypt(to_text)

            elif self.entity_num == MODE_CMU:
                #收到地面站证书
                if self.custom2_statu == C2_CMU_HELLO_SEND:
                    self.custom2_statu = C2_CMU_CERT_RECEIVED
                    processed_text = Process.messageDecode(origin_text)
                    (sym_key, enc_sym_key) = self.getSymKey(processed_text)
                    #发送公钥加密后的对称密钥
                    if sym_key is not None:
                        self._sym_key = sym_key.decode("latin1")
                        self.putMessageParas(
                            [("2", "P8", self.getArn(), "2", "", self.getId(), enc_sym_key, "")])
                        self.custom2_statu = C2_DONE
                        self._c2_done_veri_signal.emit()
                    else:
                        self.custom2_statu = C2_WAIT_HANDSHAKE

                elif self.custom2_statu == C2_DONE:
                    try:
                        to_text = Process.messageDecode(origin_text)
                        processed_text = self.symmetricDecrypt(to_text)
                    except:
                        processed_text = origin_text
        else:
            processed_text = origin_text

        msg = Message.CompleteMessage(msg_tuple +
            (origin_text, processed_text, sign_text, sign_valide, cipher_text))

        return msg
    
    def putMessageParas(self, paras_list):
        self.putMessageParasExec(paras_list, False)

    #根据安全模式进行预处理
    def putMessageParasExec(self, paras_list, isReplay):
        print(paras_list)
        for paras in paras_list:
            text = paras[6]

            processed_text = ""
            final_text = ""
            if self._sec_level == Message.Message.NORMAL or isReplay is True:
                final_text = text
            elif self._sec_level == Message.Message.CUSTOM:
                cipher_text = self.symmetricEncrypt(text)
                sign_text = self.getSign(cipher_text).decode("latin1")
                processed_text = chr(len(sign_text)) + sign_text + cipher_text
                final_text = Process.messageEncode(
                    processed_text.encode("latin1"))
            elif self._sec_level == Message.Message.CUSTOM2:
                if self.custom2_statu == C2_WAIT_HANDSHAKE:  # 针对CMU
                    self.custom2_statu = C2_CMU_HELLO_SEND
                    final_text = text
                elif self.custom2_statu == C2_DSP_HELLO_RECEIVED:  # 针对收到“hello”的DSP
                    self.custom2_statu = C2_DSP_CERT_SEND
                    final_text = Process.messageEncode(text)
                elif self.custom2_statu == C2_CMU_CERT_RECEIVED:
                    self.custom2_statu = C2_CMU_KEY_SEND
                    final_text = Process.messageEncode(text)
                elif self.custom2_statu == C2_DONE:
                    cipher_text = self.symmetricEncrypt(text)
                    final_text = Process.messageEncode(cipher_text.encode("latin1"))

            self.protocol.appendWaitsend(
                self._sec_level, paras, final_text, None)


class DSP(Entity):

    def __init__(self) -> None:
        super().__init__()
        self.work_space = self.work_space + "dsp/"
        self.entity_num = MODE_DSP
        self.custom2_statu = C2_WAIT_HANDSHAKE
        self.current_arn = None
        self.protocol = Protocol.DSPProtocol(self.entity_num, self)
        self.ca = None

    def receiveBlock(self, dict):
        msg_tuple = self.interpreteBlock(dict)
        if msg_tuple is None:
            return
        msg = Message.Message(msg_tuple)
        if self.statu == self.WAIT_START:
            self._test_signal.emit(msg, MODE_DSP)
        else:
            self._blk_signal.emit(msg, MODE_DSP)

    def receiveCompleteMsg(self, com_msg):
        ret = super().receiveCompleteMsg(com_msg)
        if ret is not None:
            self._com_signal.emit(ret, MODE_DSP)

    def getSign(self, cipher):
        super().getSign(cipher)
        return Crypto.Security.getSign("/home/jiaxv/inoproject/Acars_Security/users/dsp/dsppri.pem" + "\x00", cipher, self._cert_key)

    def verifySign(self, cipher, sign):
        super().verifySign(cipher, sign)
        return Crypto.Security.verySign("/home/jiaxv/inoproject/Acars_Security/users/cmu/cmucert.pem" + "\x00", cipher, sign)

    def setCurrentArn(self, arn):
        self.current_arn = arn

    def getCurrentArn(self):
        return self.current_arn

    def setCert(self, paras):
        self.ca.genClientCert(self.work_space, paras,
                              self.entity_num, self._cert_key)

    def setCAEntity(self, ca):
        self.ca = ca


class CMU(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.work_space = self.work_space + "cmu/"
        self.entity_num = MODE_CMU
        self.arn = None
        self.id = None
        self.custom2_statu = C2_WAIT_HANDSHAKE
        self.protocol = Protocol.CMUProtocol(self.entity_num, self)
        self.ca = None

    def receiveBlock(self, dict):
        msg_tuple = self.interpreteBlock(dict)
        if msg_tuple is None:
            return
        msg = Message.Message(msg_tuple)
        if self.statu == self.WAIT_START:
            self._test_signal.emit(msg, MODE_CMU)
        else:
            self._blk_signal.emit(msg, MODE_CMU)

    def receiveCompleteMsg(self, com_msg):
        ret = super().receiveCompleteMsg(com_msg)
        if ret is not None:
            self._com_signal.emit(ret, MODE_CMU)

    def getSign(self, cipher):
        super().getSign(cipher)
        return Crypto.Security.getSign("/home/jiaxv/inoproject/Acars_Security/users/cmu/cmupri.pem" + "\x00", cipher, self._cert_key)

    def verifySign(self, cipher, sign):
        super().verifySign(cipher, sign)
        return Crypto.Security.verySign("/home/jiaxv/inoproject/Acars_Security/users/dsp/dspcert.pem" + "\x00", cipher, sign)

    def setArnandId(self, arn, id):
        self.arn = arn
        self.id = id

    def getArn(self):
        return self.arn

    def getId(self):
        return self.id

    def setCert(self, paras):
        self.ca.genClientCert(self.work_space, paras,
                              self.entity_num, self._cert_key)

    def setCAEntity(self, ca):
        self.ca = ca


class CA(Entity):
    def __init__(self):
        super().__init__()
        self.work_space = self.work_space + "ca/"
        self.entity_num = MODE_CA

    def setCert(self, paras):
        Crypto.Security.cert_test(
            self.work_space, paras, self.entity_num, self._cert_key)

    def genClientCert(self, work_space, paras, entity_num, key):
        Crypto.Security.cert_test(work_space, paras, entity_num, key)
