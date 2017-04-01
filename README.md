# pi_heizungssteuerung
Ein Python Skript für eine Heizungssteuerung realisiert mit dem Raspberry Pi.

Zweck dieses Skripts ist es, Temperaturen der Thermostate, die anhand der Konfigurations-Datei benannt werden, auszulesen um die aktuelle Temperatur eines
Raumes festzustellen. Ebenfalls in der Konfigurations-Datei festgelegt, ist die Soll Temperatur. Ist diese groesser als der ausgelesene Wert, so wird ein Relais
aktiviert, welches die Heizung einschaltet.

Voraussetzung fuer die Funktionalitaet des Skripts ist, dass alle verwendeten gpios der Relais die direction "out" gesetzt haben. Hierfuer kann das Skript
Start.sh beim System-Start ausgefuehrt werden. Start.sh liest die gpios aus der Konfigurations-Datei aus. Eine Beispiel Konfiguration finden Sie in Konfiguration.xml
