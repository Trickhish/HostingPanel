from datetime import datetime, timezone, timedelta, date

from src.utils import *


class Course:
    basKeys = {
        "id": [],
        "name": [],
        "start": [],
        "end": [],
        "classroom": [],
        "prof_id": ["professor"],
        "present": ["student_presence"]
    }
    addKeys = {
        "class_name": ["training_name","class"],
        "class_id": ["class_id","training_id"],
        "school_id": ["school_id"]
    }
    allKeys = basKeys | addKeys

    
    def fromDt(dt):
        dtk = dt.keys()

        ndt = {}
        
        for name,keys in Course.basKeys.items():
            keys.append(name)
            for i in range(len(keys)):
                keys.append(keys[i].upper())
            
            k = next((k for k in keys if k in dtk), None)
            if (k):
                ndt[name] = dt[k]
        
        for name,keys in Course.addKeys.items():
            for i in range(len(keys)):
                keys.append(keys[i].upper())
            
            k = next((k for k in keys if k in dtk), None)
            if (k):
                ndt[name] = dt[k]
            
        ncourse = Course(ndt["id"], ndt["name"], ndt["start"], ndt["end"])

        for k,v in ndt.items():
            setattr(ncourse, k, v)

        return(ncourse)

    def __init__(self, id, name, start, end):
        self.detailed = False

        self.id = id
        self.name = name
        self.start = start
        self.end = end
    
    def completeData(self, dt):
        dtk = dt.keys()

        for name,keys in Course.allKeys.items():
            keys.append(name)
            for i in range(len(keys)):
                keys.append(keys[i].upper())

            k = next((k for k in keys if k in dtk), None)
            if (k):
                setattr(self, name, dt[k])

    def print(self):
        print(f"{self.name} ({self.id})")
        for k,v in self.__dict__.items():
            if k in ["name"]:
                continue
                
            print(f"    {k}: {v}")
    
    def prettyPrint(self):
        start = timeFromISO(self.start)
        end = timeFromISO(self.end)

        if start.strftime("%d/%m/%Y")==date.today().strftime("%d/%m/%Y"):
            sstday = "Aujourdhui"
        elif (start.day == date.today().day+1):
            sstday = "Demain"
        else:
            stday = start.strftime("%d/%m/%Y")
            sstday = f"le {stday}"
        sthour = start.strftime("%H:%M")
        edhour = end.strftime("%H:%M")

        ks = self.__dict__.keys()

        print("")
        print(f"🎓 {self.name}")
        print(f"    ID: {self.id}")
        if 'class_name' in ks:
            print(f"    Classe: {self.class_name if 'class_name' in ks else '❓'}")
        print(f"    {sstday} de {sthour} à {edhour}")
        print(f"    en {self.classroom}")
        print(f"    Présent: {'✅' if self.present else '❌'}")
        print("")
