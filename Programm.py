'''
Heizungssteuerung v 1.0
11. September 2015

Christian Weiss
Simon Sedlatschek

Zweck dieses Skripts ist es, Temperaturen der Thermostate, die anhand der
Konfigurations-Datei benannt werden, auszulesen um die aktuelle Temperatur eines
Raumes festzustellen. Ebenfalls in der Konfigurations Datei festgelegt, ist die
Soll Temperatur. Ist diese groesser als der ausgelesene Wert, so wird ein Relais
aktiviert, welches die Heizung einschaltet.

Voraussetzung fuer die Funktionalitaet des Skripts ist, dass alle verwendeten
gpios der Relais die direction "out" gesetzt haben. Hierfuer kann das Skript
Start.sh beim System-Start ausgefuehrt werden. Start.sh liest die gpios aus der
Konfigurations-Datei aus.
'''

#Importieren der benoetigten Bibliotheken
import time
from datetime import datetime
from datetime import timedelta
import xml.etree.ElementTree


#Die Konfigurations Datei im XML Format wird geladen und geparsed
e = xml.etree.ElementTree.parse("Konfiguration.xml").getroot()


'''
Laden der Einstellungen aus der Konfigurations-Datei.
"pumpe_aktiv" wird auf True gesetzt, wenn eine Pumpe angesteuert werden soll,
ist dies der Fall muss das Relais ebenfalls gesetzt sein.
"ist_speicher" wird auf True gesetzt, wenn die ausgelesenen Ist-Werte in
einzelnen Dateien im Verzeichnis /ist gespeichert werden sollen.
'''
pumpe_aktiv = e.find("pumpe").find("aktiv").text.lower()
print ("Einstellung: pumpe_aktiv=%s" % (pumpe_aktiv))
ist_speichern = e.find("einstellungen").find("ist_speichern").text.lower()
print ("Einstellung: ist_speichern=%s" % (ist_speichern))

'''
Alle Raeume, welche in der Konfigurations Datei definiert wurden, werden hier
in einer Schleife durchlaufen, wobei die Variable "raum" fuer den Raum des
aktuellen Durchlaufs steht.
'''
for raum in e.findall("raum"):
 #Fuer eine bessere Uebersicht wird der Name des Raums ausgegeben
 print ("\nRaum %s" % (raum.attrib))

 '''
 Der Standard-Wert der Variable "fehler" ist "True", da die darauffolgende
 Schleife solange durchlaufen werden soll, bis der Ist Wert ohne Fehler
 ausgelesen werden konnte.
 '''
 fehler = True
 while fehler:

  '''
  Der Pfad des Sensors zum Auslesen der Temperatur wird hier aus der
  Konfigurations-Datei ausgelesen.
  '''
  sensor = raum.find("sensor").text

  #Fuer eine bessere Uebersicht wird der Pfad des Sensors ausgegeben
  print ("Sensor: %s" % (sensor))

  '''
  Der Inhalt der Sensor-Datei sieht beispielsweise so aus:
  37 01 4b 46 7f ff 09 10 26 : crc=26 YES

  37 01 4b 46 7f ff 09 10 26 t=19437

  Die Temperatur in diesem Fall betraegt 19,43 Grad Celcius. Im folgendem Code
  wird Zeile fuer Zeile ausgelesen, und der Inhalt beim "=" Zeichen getrennt
  und in das Array "zuordnung" gespeichert. Das Array sieht also so aus:
  1. Durchlauf
  zuordnung[0]: 37 01 4b 46 7f ff 09 10 26 : crc
  zuordnung[1]: 26 YES
  2. Durchlauf
  zuordnung[0]: 37 01 4b 46 7f ff 09 10 26 t
  zuordnung[1]: 19437
  Da nur "zuordnung[1]" des zweiten Durchlaufs benoetigt wird, wird die Variable
  "ist_m1" einfach ueberschrieben. "ist_m1" steht fuer Ist-Temperatur-Messung-1.
  Da es gelegentlich zu unplausiblen Messergebnissen kommt, ist es notwendig,
  zwei Messungen durchzufuehren, um danach eine Plausibilitaetspruefung
  vollziehen zu konnen.
  '''
  fobj = open(sensor, "r")
  for line in fobj:
   zuordnung = line.split("=")
   ist_m1 = zuordnung[1]
  fobj.close()

  #Zwischen den zwei Messungen wird eine Millisekunde gewartet.
  time.sleep(1)

  '''
  Gleicher Vorgang wie bereits erklaert, dieses Mal wird des Ergebnis jedoch in
  "ist_m2" gespeichert.
  '''
  fobj = open(sensor, "r")
  for line in fobj:
   zuordnung = line.split("=")
   ist_m2 = zuordnung[1]
  fobj.close()

  '''
  Da es sich bei den ausgelesenen Messwerten um Strings handelt, muessen diese
  in Integer umgewandelt werden, um mathematische Funktionen zu ermoeglich.
  '''
  int_ist_m1 = int(ist_m1)
  int_ist_m2 = int(ist_m2)

  '''
  Die Messwerte werden ohne Komma ausgelesen, welches durch das Teilen durch
  1000.0 gesetzt werden.
  '''
  ist_g1 = (int_ist_m1 / 1000.0)
  ist_g2 = (int_ist_m2 / 1000.0)

  '''
  Die Messwerten werde auf zwei Nachkommastellen gerundet. "ist_g1" steht fuer
  Ist-Temperatur-Gerundet-1.
  '''
  ist_g1 = round(ist_g1, 2)
  ist_g2 = round(ist_g2, 2)

  '''
  Fuer eine bessere Uebersicht, werden die beiden gerundeten Messwerte
  ausgegeben.
  '''
  print ("ist_g1 = %s" % (ist_g1))
  print ("ist_g2 = %s" % (ist_g2))

  '''
  Die Pruefsumme "pruef" wird durch einfaches Teilen der beiden Messwerte
  errechnet. Im optimalen Fall betraegt diese den Wert 1, und beide Messungen
  ergaben die gleichen Werte.
  '''
  pruef = (ist_g1 / ist_g2)

  #Fuer eine bessere Uebersicht wird die Pruefsummer ausgegeben
  print ("pruef = %s" % (pruef))

  '''
  Dieser Abschnitt beeinhaltet die Plausibilitaetspruefung. Die Pruefsummer darf
  nicht zu weit vom Wert 1 abweichen, da zwei Messungen im Abstand von einer
  Millisekunde keine zu unterschiedlichen Werte ausgeben duerfen. Ist dies
  dennoch der Fall ist von einem Fehler auszugehen und die Variable "fehler"
  wird nicht auf "False" gesetzt, wodurch die Schleife erneut ausgefuehrt wird.
  '''
  #Die Messergebnise sind nicht plausibel wenn...
  if not (pruef > 1.027): #... die Pruefsumme groesser als 1.027 ist
   if not (pruef < 0.977): #... die Pruefsummer kleiner als 0.977 ist

    '''
    Es ist nicht notwendig g2 zu pruefen, da durch das Testen der Pruefsumme
    sichergestellt ist, dass beide aehnliche Werte enthalten.
    '''
    if not (ist_g1 > 100): #... die beiden Werte ueber 100 grad betragen
     if not (ist_g1 < 0): #... die beiden Werte unter 0 grad betragen

      '''
      In der Konfigurations-Datei kann festgelegt werden, ob die Ist werte im
      Verzeichnis /ist gespeichert werden sollen.
      '''
      if ist_speichern == "true":
       f = open('ist/%s' % (sensor.split('/')[5]), 'w')
       f.write(str(ist_g1))
       f.close

      '''
      Wenn die Plausibilitaetspruefung bestanden wird, kann davon ausgegangen
      werden, dass kein Fehler mehr besteht. Die Variable "fehler" wird auf
      "False" gesetzt. Das Programm steigt somit aus der Schleife aus. Es sind
      keine weiteren Messungen in diesem Raum erforderlich.
      '''
      fehler = False

 '''
 Die Variable "soll_temperatur" wird spaeter zur Errechnung der Notwendigkeit
 des Heizens verwendet. Der Standard-Wert betraegt 0. Wird also kein soll-Wert
 aus der Konfigurations-Datei ausgelesen wird nicht geheizt. (Ausser im extremen
 Fall, wenn es unter 0 Grad Celcius um Haus hat, aber dann sollte sowieso
 geheizt werden).
 '''
 soll_temperatur = 0

 '''
 Diese Schleife durchlaeuft alle angelegt Soll-Zonen des Raums aus der
 Konfigurations Datei.
 '''
 for soll in raum.findall("soll"):

  '''
  Es werden drei Zeiten definiert.
  "jetzt" entspricht der aktuellen Uhrzeit.
  "start" entspricht der Startuhrzeit, ausgelesen aus der Konfigurations Datei.
  "ende" entspricht der Endeuhrzeit, ausgelesen aus der Konfigurations Datei.
  Die Variable "temperatur" beeinhaltet die Temperatur, die fuer diese Soll-Zonen
  festgelegt wurde.
  '''
  jetzt = datetime.time(datetime.now())
  start = datetime.time(datetime.strptime(soll.find("start").text, "%H:%M"))
  ende = datetime.time(datetime.strptime(soll.find("ende").text, "%H:%M"))
  temperatur = float(soll.find("temperatur").text)

  #Fuer eine bessere Uebersicht werden die drei Variable ausgegeben.
  print ("Soll Zeit von %s Uhr bis %s Uhr mit der Temperatur %s" % (start, ende, temperatur))

  if ende == start:
   '''
   Wenn die Ende und Start Zeit gleich sind, wird davon ausgegangen, dass sich
   die Soll-Zone ueber den ganzen Tag erstreckt, weshalb "soll_temperatur" der
   Temperatur der Zone zugewiesen wird.

   Beispiel:
   "jetzt": 08:00 Uhr
   "start": 00:00 Uhr
   "ende": 00:00 Uhr
   Ergebnis: positiv
   '''
   soll_temperatur = temperatur

  if ende > start and start < jetzt and ende > jetzt:
   '''
   Wenn die Ende-Zeit groesser ist, als die Start-Zeit und die Jetzt-Zeit
   dazwischen liegt, dann kann die "soll_temperatur" der Temperatur der Zone
   zugewiesen werden.

   Beispiel 1:
   "jetzt": 08:00 Uhr
   "start": 06:00 Uhr
   "ende": 20:00 Uhr
   Ergebnis: positiv

   Beispiel 2:
   "jetzt": 05:00 Uhr
   "start": 06:00 Uhr
   "ende": 20:00 Uhr
   Ergebnis: negativ
   '''
   soll_temperatur = temperatur

  if ende < start and jetzt > start:
   '''
   Wenn die Ende-Zeit kleiner als die Start-Zeit ist, so liegt das Ende der Zone
   erst im naechsten Tag. Weshalb nur zu Pruefen ist, ob die Jetzt-Zeit groesser
   als die Start-Zeit ist.

   Beispiel 1:
   "jetzt": 10:00 Uhr
   "start": 08:00 Uhr
   "ende": 00:00 Uhr
   Ergebnis: positiv

   Beispiel 2:
   "jetzt": 07:00 Uhr
   "start": 08:00 Uhr
   "ende": 00:00 Uhr
   Ergebnis: negativ
   '''
   soll_temperatur = temperatur

  if ende < start and jetzt < ende:
   '''
   Wenn die Ende-Zeit kleiner als die Start-Zeit ist, so liegt das Ende der Zone
   erst im naechsten Tag. Wenn aber die Ende-Zeit noch groesser ist als die
   Jetzt-Zeit, dann ist der neachste Tag schon eingetreten. Weshalb nur zu
   pruefen ist, ob die Jetzt-Zeit kleiner als die Ende-Zeit ist.

   Beispiel 1:
   "jetzt": 05:00 Uhr
   "start": 20:00 Uhr
   "ende": 08:00 Uhr
   Ergebnis: positiv

   Beispiel 2:
   "jetzt": 09:00 Uhr
   "start": 20:00 Uhr
   "ende": 08:00 Uhr
   Ergebnis: negativ
   '''
   soll_temperatur = temperatur

 #Fuer eine bessere Uebersicht wird die ermittelte Soll-Temeratur ausgegeben.
 print ("Aktive Soll-Temperatur ist %s" % (soll_temperatur))

 '''
 Die Variable "relais" wird definiert mit dem Wert, welcher fuer diesem Raum
 in der Konfigurations Datei fuer das Attribut "relais" festgelegt wurde. Wenn
 der Soll-Wert groesser als der Ist-Wert ist, wird das Relais aktiviert,
 ansonten wird es deaktiviert (sofern es ueberhaupt aktiviert war). Sobald ein
 Relais angesteuert wird, wird die Pumpe (sofern aktiv) benoetigt. Hierfuer
 wird die Variable "pumpe_benoetigt" verwendet.
 '''
 pumpe_benoetigt = False;
 relais = raum.find("relais").text
 f = open("/sys/class/gpio/gpio%s/value" % (relais), "w")
 if ist_g1 < soll_temperatur:
  f.write("1")
  pumpe_benoetigt = True;
  #Fuer eine bessere Uebersicht wir das Ergebnis des Skripts ausgegeben
  print ("Ist %s kleiner als Soll %s, Relais %s aktiviert" % (ist_g1, soll_temperatur, relais))
 else:
  f.write("0")
  #Fuer eine bessere Uebersicht wird das Ergebnis des Skripts ausgegeben
  print ("Ist %s groesser als Soll %s, Relais %s deaktviert" % (ist_g1, soll_temperatur, relais))
 f.close

 '''
 Wenn eine Pumpe benoetigt wird, wird diese in diesem Schritt aktiviert.
 '''
if pumpe_aktiv == "true":
 if pumpe_benoetigt == True:
  relais_pumpe = e.find("pumpe").find("relais").text
  #Fuer eine bessere Uebersicht wird der Pumpen Status ausgegeben
  print ("\n\nPumpe wird benoetigt. Relais %s aktiviert." % (relais_pumpe))
  f = open("/sys/class/gpio/gpio%s/value" % (relais_pumpe), "w")
  f.write("1")
  f.close
 else:
  #Fuer eine bessere Uebersicht wird der Pumpen Status ausgegeben
  print ("\n\nPumpe wird nicht benoetigt.")
