from cryptography.fernet import Fernet

x = Fernet('SEhrVAIY16ROnOWOKXdk7XaUTPn-_sheDIqHaWfWOKY=')


class Secrets:
    def __init__(self):
        self.key = b'gAAAAABkw_S1Xcmc12aIQObWePRmQg-JIIXHi63OLo__9MuYPMgPwgnbgt32o5dyzp88bFTRqantxyjEBLrOUdbay8O0oavwHe9DR_u5b6sfYBUd0I9fAwc5y-L8S6I5MA3knKECzwqm'
        self.pas = b'gAAAAABkw_TnzJWEZvSRCacVzfBSs_Dv77u3LpPXSkHDXRSS89zJn52MojZqMUTwZ6c_Z-Q95gEVsNioUf82iaPp-fW85zkH2nyeVP4nLxMnRAdXQeQlSpY4DZUFgjU94nGjE2ufT709'

    def id(self):
        return str(x.decrypt(self.key), 'utf-8')

    def password(self):
        return str(x.decrypt(self.pas), 'utf-8')
