from dotenv.main import dotenv_values
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Union
from twilio.rest import Client
from os import environ
from dotenv import load_dotenv, dotenv_values
import webbrowser

load_dotenv()

envValues: Dict[str, str] = dotenv_values('.env')

accountSID: str = envValues['TWILIO_ACCOUNT_SID']
authToken: str = envValues['TWILIO_AUTH_TOKEN']
myPhoneNumber: str = envValues['MY_PHONE']
botPhoneNumber: str = envValues['BOT_PHONE']

rootUrl: str = 'https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-'


class CheckAvailability():
    def __init__(self, rootUrl: str) -> None:
        self.rootUrl: str = rootUrl
        self.headers: Dict[str, str] = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.170'}
        self.keepChecking: bool = True
        self.accountSID: str = accountSID
        self.authToken: str = authToken
        self.client: object = Client(self.accountSID, self.authToken)
        self.pageInfoDict: Dict[int, str] = {158431: 'Arena Berlin', 158434: 'Messe Berlin / Halle 21',
                                             158437: 'Erika-Heß-Eisstadion', 158435: 'Velodrom Berlin', 158436: 'Flughafen Berlin-Tegel'}

    def getPageContent(self) -> List[Union[str, int]]:
        pageContentList: List[Union[str, int]] = []

        try:
            for key in self.pageInfoDict.keys():
                fullUrl: str = f'{self.rootUrl}{key}'

                page: object = requests.get(fullUrl, headers=self.headers)
                soup: object = BeautifulSoup(page.content, features='lxml')

                pageText: str = soup.get_text()

                pageContentList.append([pageText, key])

        except:
            self.main()

        return pageContentList

    def main(self, sendSMS: bool) -> bool:
        while self.keepChecking:
            pageContent: List[Union[str, int]] = self.getPageContent()

            for index in range(len(pageContent)):
                if 'Keine Verfügbarkeit in dieser Woche' not in pageContent[index][0]:
                    key: int = pageContent[index][1]
                    if sendSMS:
                        self.client.api.account.messages.create(
                            to=myPhoneNumber,
                            from_=botPhoneNumber,
                            body=f'Termin Verfügbar in {self.pageInfoDict[key]} Link: {self.rootUrl}{key}')

                    else:
                        webbrowser.open(f'{self.rootUrl}{key}')

                    self.keepChecking: bool = False

        return True


if __name__ == '__main__':
    CheckAvailability(rootUrl).main()
