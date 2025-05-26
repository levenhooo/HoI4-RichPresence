import os
import sys
import json
import time
import psutil
import pypresence
from Countries import CountryDict

class RichPresence():
    client_id = 1371224044380225638
    client = pypresence.Presence(client_id)
    HoI4_User_Directory = ""
    HoI4_RichPresence_Path = ""

    def GetConfig():
        CommonPath_RP = f"C:\\Users\\{os.getlogin()}\\Documents\\Paradox Interactive\\Hearts of Iron IV\\RichPresence\\"
        if os.path.exists(path=CommonPath_RP) == False:
            found_config = False
            while found_config == False:
                manual_path = input("Common Rich Presence path doesn't exist. Please enter the path manually: ")
                if os.path.exists(path=manual_path):
                    if "config.json" in os.listdir(path=manual_path):
                        #Load config
                        with open(file=f"{manual_path}\\config.json", mode="r") as file:
                            config = json.load(fp=file)
                        RichPresence.HoI4_User_Directory = config["HoI4_User_Directory"]
                        RichPresence.HoI4_RichPresence_Path = config["HoI4_RichPresence_Path"]
                        found_config = True
                    else:
                        print("Rich Presence path doesn't contain the config.json, please try again.")
                        continue
                else:
                    continue
        else:
            #Load config.json
            with open(file=f"{CommonPath_RP}\\config.json", mode="r") as file:
                config = json.load(fp=file)
            RichPresence.HoI4_User_Directory = config["HoI4_User_Directory"]
            RichPresence.HoI4_RichPresence_Path = config["HoI4_RichPresence_Path"]

    def GetLatestSaveGame():
        RichPresence.GetConfig()
        SaveGamePath = f"{RichPresence.HoI4_User_Directory}\\save games"
        if os.path.exists(path=SaveGamePath):
            #Get all savegame files
            Files = os.listdir(path=SaveGamePath)
            #Check if there are any files ending with .hoi4
            if len(Files) == 0:
                return 0
            SaveGameFiles = []
            for savegame in Files:
                if savegame.endswith(".hoi4"):
                    SaveGameFiles.append(savegame)
            #Check if there are any .hoi4 files
            if len(SaveGameFiles) == 0:
                return 0
            #Get latest modified file
            Last_Modifications = []
            for latest_savegame in SaveGameFiles:
                Last_Modifications.append(os.path.getmtime(filename=f"{SaveGamePath}\\{latest_savegame}"))
            last_modified = max(Last_Modifications)
            index = Last_Modifications.index(last_modified)
            LastSaveGame = SaveGameFiles[index]
            return f"{SaveGamePath}\\{LastSaveGame}"
        else:
            print("You seem to be missing a save games folder. Did you install the game correctly?")
            input("Press any key to exit..")
            sys.exit(0)

    def ReadLatestSaveGame():
        LastSaveGameFile = RichPresence.GetLatestSaveGame()
        if LastSaveGameFile == 0:
            return 0
        data = []
        CleanedUp = False
        #Try to get the first 15 lines and add it to a list
        try:
            with open(file=LastSaveGameFile, encoding="utf-8", mode="r") as SaveGameFile:
                for i, line in enumerate(SaveGameFile):
                    if i >= 15:
                        break
                    data.append(line)
        except:
            print("Couldn't read the savegame. Did you execute the setup?")
            input("Press any key to exit..")
            sys.exit(0)
        new_data = []
        #Remove specific chars
        for element in data:
            x1 = element.replace("\n", "")
            x2 = x1.replace("\t", "")
            new_data.append(x2)
        #Only keep needed data = nation, ideology, year
        while CleanedUp != True:
            try:
                new_data.pop(0)
                for i in range(0, 11):
                    new_data.pop(3)
            except:
                print("Something went wrong while reading the latest savegame.")
            CleanedUp = True
        #Extract needed data
        CleanUp_FE = new_data[0].replace('player="', '').replace('"', '')
        CleanUp_SE = new_data[1].replace('ideology=', '')
        CleanUp_TE = new_data[2].replace('date="', '')[:4]
        new_data[0] = CleanUp_FE
        new_data[1] = CleanUp_SE
        new_data[2] = CleanUp_TE
        return new_data
    
    def UpdatePresence():
        data = RichPresence.ReadLatestSaveGame()
        CountryName = ""
        Ideology = ""
        #Check if SaveGame exists, if not => Try again in 60 seconds
        if data == 0:
            RichPresence.client.update(details="Starting the game..", large_image="hoi4_logo") #CHANGE MORE PARAMETERS
            time.sleep(60)
        elif data != 0:
            if data[1] == "democratic":
                Ideology = "Democratic"
            if data[1] == "communism":
                Ideology = "Communism"
            if data[1] == "fascism":
                Ideology = "Fascism"
            if data[1] == "neutrality":
                Ideology = "Neutrality"
            CountryName = CountryDict.Dict[data[0]][Ideology]
            print("Data[0]: ", data[0])
            print("Ideology:", Ideology)
            if Ideology == "Democratic":
                Ideology = "Democratic"
            if Ideology == "Neutrality":
                Ideology = "Non-Aligned"
            Flag = data[0].lower()
            RichPresence.client.update(details="Playing as " + CountryName + " in " + data[2], state="Ideology: " + Ideology, large_image=Flag)
            time.sleep(120)
        else:
            print("Something went wrong. What did you do?")
            input("Press any key to exit..")
            sys.exit(0)

    def CheckIfGameIsRunning():
        process_name = "hoi4.exe"
        for process in psutil.process_iter(["name"]):
            if process.info["name"] == process_name:
                return True
        return False

    def Initialize():
        RichPresence.client.connect()
        GameRunning = True
        #Check if game is still running
        while GameRunning:
            GameRunning = RichPresence.CheckIfGameIsRunning()
            if GameRunning != True:
                break
            RichPresence.UpdatePresence()
        RichPresence.client.close()

RichPresence.Initialize()
