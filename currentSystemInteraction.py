#TODO:
# Add a way to display ship and waypoint data in the actual UI - use tkinter notebook?

import tkinter as tk
from tkinter import ttk
import requests
import math

token = open("token.txt", "r").read()
headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {token}"}
baseURL = "https://api.spacetraders.io/v2/"

#Get system data
systemData = None
waypointsInSystem = {}
waypointSymbols = []
selectedWaypoint = None
response = requests.get(f"{baseURL}systems/X1-XJ17/waypoints",headers=headers)
systemData = response.json()["data"]
for i in systemData:
        waypointsInSystem[i['symbol']] = i
        waypointSymbols.append(i['symbol'])

#Get ship data
shipData = None
selectedShip = None
fleetData = {}
shipSymbols = []
response = requests.get(f"{baseURL}my/ships", headers=headers)
shipData = response.json()["data"]
for i in shipData:
     fleetData[i['symbol']] = i
     shipSymbols.append(i['symbol'])
shipLocation = None
selectedShip = shipSymbols[0]
#Functions for Buttons
def viewWaypoint():
        print(waypointsInSystem[selectedWaypoint])
def viewMarket():
        waypoint = waypointsInSystem[selectedWaypoint]
        for trait in waypoint["traits"]:
            if trait["symbol"] == 'MARKETPLACE':
                response = requests.get(f"{baseURL}systems/{waypoint['systemSymbol']}/waypoints/{waypoint['symbol']}/market",headers=headers)
                print(f"You can sell the following at {waypoint['symbol']}:")
                for good in response.json()["data"]["imports"]:
                    print(good["symbol"])
                print("\n")
                return
        print("No market trade on this waypoint")
        return
def viewShipInfo():
     print(fleetData[selectedShip])
##Create GUI

def getFlightFuelCost(destination):
     currentWaypoint = fleetData[selectedShip]['nav']["waypointSymbol"]
     currentCoords = [waypointsInSystem[currentWaypoint]['x'],waypointsInSystem[currentWaypoint]['y']]
     destinationCoords = [waypointsInSystem[destination]['x'],waypointsInSystem[destination]['y']]
     distance = math.sqrt((currentCoords[0]-destinationCoords[0])**2 + (currentCoords[0]-destinationCoords[0])**2) #euclidean distance
     cruiseFuelCost = round(distance)
     return cruiseFuelCost

def checkFlightValidity(destination):
     if destination == fleetData[selectedShip]['nav']["waypointSymbol"]:
          return "Ship is already at this waypoint"
     requiredFuel = getFlightFuelCost(destination)
     currentFuel = fleetData[selectedShip]['fuel']['current']
     if  currentFuel <= requiredFuel:
          return f"Not enough fuel, the ship has {currentFuel} units, and the trip requires {requiredFuel} units"
     else:
          return f"Trip is possible, the ship has {currentFuel} units, and the trip requires {requiredFuel} units"
class MainApplication(tk.Tk):
     def __init__(self, *args, **kwargs):
          tk.Tk.__init__(self, *args, **kwargs)

          self.title("Space Traders API")
          self.geometry("400x300")
          self.container = tk.Frame(self)
          self.container.pack(side="top", fill="both", expand=True)
          self.container.grid_rowconfigure(0, weight=1)
          self.container.grid_columnconfigure(0, weight=1)
          self.screens = {}
          for screenClass in (startScreen, waypointScreen):
               screenName = screenClass.__name__
               screen = screenClass(parent = self.container, controller = self)
               self.screens[screenName] = screen
               screen.grid(row=0, column=0, sticky="nsew")
          self.showScreen("startScreen")

     def showScreen(self, pageName):
            screen = self.screens[pageName]
            screen.tkraise()

class startScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        global selectedShip
        global shipLocation
        shipLocation = tk.StringVar()
        shipLocation.set(f"{fleetData[selectedShip]['nav']['waypointSymbol']}")

        label = ttk.Label(self, text="Ship Information")
        label.pack(pady=10, padx=10)

        def on_select(event):
            global selectedShip
            selectedShip = shipDropDown.get()
            global shipLocation
            shipLocation.set(f"{fleetData[selectedShip]['nav']['waypointSymbol']}")

        #Change Selected Ship
        shipDropDown = ttk.Combobox(self, values = shipSymbols, state="readonly")
        shipDropDown.pack(pady=10)
        shipDropDown.set(shipSymbols[0])
        selectedShip = shipSymbols[0]
        shipDropDown.bind("<<ComboboxSelected>>", on_select)


        button = ttk.Button(self, text = "View Ship Info", command = viewShipInfo)
        button.pack(pady = 5)
        button = ttk.Button(self, text="View System's Waypoint Information", command=lambda: controller.showScreen("waypointScreen"))
        button.pack(pady = 5)

class waypointScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, textvariable=shipLocation)
        label.pack(pady=10, padx=10)

        #Dropdown Box
        def on_select(event):
            global selectedWaypoint 
            selectedWaypoint = combobox.get()
            print(selectedWaypoint)


        combobox = ttk.Combobox(self, values = waypointSymbols, state="readonly")
        combobox.pack(pady=10)
        combobox.set(waypointSymbols[0])
        global selectedWaypoint
        selectedWaypoint = waypointSymbols[0]
        combobox.bind("<<ComboboxSelected>>", on_select)


        #Buttons
     
        button = tk.Button(self,text="View Waypoint Info",command = viewWaypoint)
        button.pack(pady = 5)
        button = tk.Button(self,text="See What You Can Sell at Waypoint",command = viewMarket)
        button.pack(pady = 5)
        button = tk.Button(self, text = "Are you able to travel to this waypoint?", command=lambda: print(checkFlightValidity(selectedWaypoint)))
        button.pack(pady = 5)
        button = ttk.Button(self, text="Go Back", command=lambda: controller.showScreen("startScreen"))
        button.pack()





app = MainApplication()
app.mainloop()



