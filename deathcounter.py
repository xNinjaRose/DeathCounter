import sys
import os
from getkey import getkey 

class DeathCounter():
    def __init__(self):
        self.deaths = 0

    def IncreaseDeath(self):
        self.deaths += 1
        return self.deaths

    def ResetDeath(self):
        self.deaths = 0
        return self.deaths

    def DecreaseDeath(self):
        if self.deaths > 0:
            self.deaths -=  1
            return self.deaths
        else: 
            self.deaths = 0
            return self.deaths 
    
    def PrintDeath(self):
        print(f"Death Count: {self.deaths}")

def DeathCount(death,DEATH_NAME):

    # d = open ("deaths.txt","w")

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print ("####################")
        print (f"  {DEATH_NAME}: {death} ")
        print ("####################")
        print ("    * + : increase *      ")
        print ("    * - : decrease *      ")
        print ("    * r : reset    *      ")
        print ("    * q : quit     *      ")
        print ("####################")
        print(">>")
        choice = getkey()
        
        if choice == "+":
            death = death0.IncreaseDeath()
            d = open ("deaths.txt","w")
            d.write(f"{DEATH_NAME} : {death} ")
            d.close()
        elif choice.lower() == "-":
            death = death0.DecreaseDeath()
            d = open ("deaths.txt","w")
            d.write(f"{DEATH_NAME} : {death} ")
            d.close()
        elif choice.lower() == "r":
            death = death0.ResetDeath()
            d = open ("deaths.txt","w")
            d.write(f"{DEATH_NAME} : {death} ")
            d.close()
        elif choice.lower() == "q":
            sys.exit()
        else: 
            print ("Invalid Input! Please Try Again!")

if __name__ == "__main__":
    death0 = DeathCounter()

    DEATH_NAME = input("How do you want to show death counter? Example: Death Count, Deaths, etc. : ")

    DeathCount(death0.deaths,DEATH_NAME)



