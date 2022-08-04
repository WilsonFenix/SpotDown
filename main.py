from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import time
import pandas as pd
import urllib.parse
from pytube import YouTube

class Spotdown:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.playlist = {
            "musica":[],
            "cantor":[]
        }
        self.driver = Chrome(executable_path="chromedriver.exe")
        self.dfPlaylist = pd.DataFrame(self.playlist)
    
    def login(self):
        self.driver.implicitly_wait(20)
        self.driver.get("https://open.spotify.com")

        #click in login button 
        login_button = self.driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[1]/header/div[5]/button[2]')
        login_button.click()

        #input email and password
        username_input = self.driver.find_element(By.XPATH, '//*[@id="login-username"]')
        userpassword_input = self.driver.find_element(By.XPATH, '//*[@id="login-password"]')
        username_input.send_keys(self.email)
        userpassword_input.send_keys(self.password)

        #click in login button
        submitbutton = self.driver.find_element(By.XPATH, '//*[@id="login-button"]')
        submitbutton.click()

    def get_the_favorites_list(self) -> dict:
        # go to favorites page
        self.driver.get("https://open.spotify.com/collection/tracks")

        #zoom out the page
        self.driver.execute_script("document.body.style.zoom = '0.01'")
        self.driver.execute_script("window.scrollBy(0, 1000);")

        #wait for the page to load
        time.sleep(60)

        #get hml code
        bspage = BeautifulSoup(self.driver.page_source, features="html.parser")
        
        for musica in bspage.find_all("div", {"class":"iCQtmPqY0QvkumAOuCjr"}):
            nome_musica = musica.find("a",{"class":"t_yrXoUO3qGsJS4Y6iXX"}).get_text()
            nome_cantor = musica.find("span",{"class":"Type__TypeElement-goli3j-0 eDbSCl rq2VQ5mb9SDAFWbBIUIn standalone-ellipsis-one-line"}).get_text()
            
            self.playlist["musica"].append(nome_musica)
            self.playlist["cantor"].append(nome_cantor)
        return self.playlist
    
    def find_music(self,nome_musica, nome_cantor):
        query = urllib.parse.quote_plus(f"{nome_musica}, {nome_cantor}")
        self.driver.get(f"https://www.youtube.com/results?search_query={query}")
        time.sleep(15)
        bspage = BeautifulSoup(self.driver.page_source) 
        video = bspage.find("a", {"id":"video-title"})
        for tentative in range(3):
            result = self.download_video("https://www.youtube.com" + video["href"], nome_musica)
            if result:
                print("Task Complete!")
            elif tentative == 2:
                print("Some Error!")

    def download_video(self,link, file_name):
        SAVE_PATH = "./playlist" #to_do 
        
        try: 
            # object creation using YouTube
            # which was imported in the beginning 
            yt = YouTube(link) 
            yt.streams.filter(abr="160kbps", progressive=False).first().download(filename=SAVE_PATH + "/" + file_name+ ".mp3")
            print(link)
        except: 
            print("Connection Error") #to handle exception 
            return False
        return True 

    def end(self):
        self.driver.close()
    
    def create_DataFrame(self):
        self.dfPlaylist = pd.DataFrame(self.playlist)
        self.dfPlaylist.to_csv("spotDown.csv")

    def dowload_music_by_csv(self):
        self.dfPlaylist = pd.read_csv("spotDown.csv")
        self.dfPlaylist = self.dfPlaylist[self.dfPlaylist.columns[1:]]

        self.dfPlaylist.apply(lambda linha: self.find_music(linha["musica"], linha["cantor"]), axis = 1 )


app = Spotdown("your_email@email.com", "your_password")

#get playlist
#app.login()
#time.sleep(10)
#app.get_the_favorites_list()
#app.create_DataFrame()

#download musics
app.dowload_music_by_csv()

app.end()
