I = 0

def gci():
    global I
    I += 1
    return I

class STEPS:
    class AUTH:
        AUTH = gci()
        PASSCODE = gci()
        FINISH = gci()

    class MENU:
        SMM_FORWARDER = gci()
        WEB_SEARCH = gci()
    
    class SMM_FORWARDER:
        class LIST:
            ENTRY = gci()
            ADD_GROUP = gci()
            ADD_GROUP_SELECT = gci()
            DEL_GROUP = gci()
            DEL_GROUP_SELECT = gci()
            SHOW_GROUP = gci()
            SITES_DELETE = gci()
            SITES_DELETE_SELECT = gci()
            SITES_ADD = gci()
            SITES_ADD_SELECT = gci()
            GROUP_SET_CRED = gci()
            CRED_USERNAME = gci()
            CRED_PASSWORD = gci()

        class TICKET:
            ENTRY = gci()
            GROUP = gci()
            SUBJECT = gci()
            TEXT = gci()
            CONFIRM = gci()

        BALANCE = gci()
    
    class WEB_SEARCH:
        ENTRY = gci()
        QUERY = gci()
        COUNTRY = gci()
        PAGES = gci()
        PROCEED = gci()

    class MAIL_PARSER:
        ENTRY = gci()
        PROCEED = gci()

    class MAIL_SENDER:
        ENTRY = gci()
        PROCEED = gci()