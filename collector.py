from bs4 import BeautifulSoup
import sys, imaplib, getpass, email, datetime, re, io, json, time

dictLinks = {}
monthList = ["jan", "feb", "mar", "apr", "may", "jun", 
            "jul", "aug", "sep", "oct", "nov", "dec"]

def parseDate(rawDate):
    parseDate = email.utils.parsedate_tz(rawDate)
    timeVal = email.utils.mktime_tz(parseDate)
    date = datetime.datetime.fromtimestamp(timeVal)

    return str(date.month) + "-" + str(date.day) + "-" + str(date.year)

def fetchAllLinks(data):

    splitData = data[0].split()

    for idx, num in enumerate(splitData):
        status, fetchedMail = mail.fetch(num, '(RFC822)')

        if status != "OK":
            print "Error occurred fetching mail. Now exiting."
            return

        message = email.message_from_string(fetchedMail[0][1])
        date = parseDate(message["Date"])
        
        if message.is_multipart():

            for elementSet in message.get_payload():
                if elementSet.get_content_charset() is None:
                    continue

                if elementSet.get_content_type() == 'text/html':
                    payload = elementSet.get_payload(decode=True)
                    charset = elementSet.get_content_charset()
                    html = (unicode(payload, str(charset), "ignore").
                        encode('utf8', 'replace')).strip()
                    soup = BeautifulSoup(html)
                    
                    valDict = {}
                    for link in soup.find_all("a"):
                        link = str(link.get("href"))
                        if "www.instantpresenter.com/aacm" in link:
                            valDict["link"] = link

                    if "link" in valDict:
                        urlcode = re.search(r'\w*$',valDict["link"]).group()
                        valDict["code"] = urlcode

                        dictLinks[date] = valDict
                    
        
        print "\rCompleted: %d/%d" % (idx+1, len(splitData)),
        sys.stdout.flush()

        time.sleep(1)

def loginAndSearchMail():
    try:
        emailAddress = raw_input("Email address: ")
        mail.login(emailAddress.strip(),getpass.getpass())
        mail.select(mailbox='INBOX', readonly=True)

        print ("Since what date do you want to look for links? Enter date in the following "
                "format: 01-Sep-2015. Leave this blank if you want to search without a time filter.")
        while True:
            inputDate = raw_input("Enter date: ")
            
            matchedDate = re.match(r'(\d{2})-([A-Za-z]{3})-(\d{4})', inputDate)

            if len(inputDate.strip()) == 0 or (matchedDate and matchedDate.group(2).lower() in monthList):
                dateFilter = "" if len(inputDate.strip()) == 0 else " SINCE " + matchedDate.group()
                status, data = mail.search(None, '(FROM "maryjohnsonkhan@gmail.com"' + dateFilter + ")")
                break
                
        if status == "OK":
            fetchAllLinks(data)
            with open("./dataLinks.json", "w") as outfile:
                json.dump(dictLinks, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
                print "\nTotal of", len(dictLinks), "links found and written to the file. Success!"

        else:
            mail.close()
            mail.logout()
            print "No messages found!"
         
    except imaplib.IMAP4.error:
        print "LOGIN FAILED!!!"

if __name__ == "__main__":

    while True:
        print "\n1: Yahoo! Mail\t\t2: Gmail"

        selectionNum = raw_input("Select your primary email provider:")

        if not selectionNum.isdigit() or int(selectionNum) > 2 or int(selectionNum) < 1:
            print "***  Your selection must be a digit from the given choices  ***"
        else:
            if selectionNum == "1":
                mail = imaplib.IMAP4_SSL('imap.mail.yahoo.com')
            elif selectionNum == "2":
                mail = imaplib.IMAP4_SSL('imap.gmail.com')
            
            loginAndSearchMail()
            break
        

