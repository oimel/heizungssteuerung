#!/bin/sh
echo -e "HEIZUNGSSTEUERUNG v1.0 START SKRIPT\n***********************************\n"

echo "1-wire Modul wird geladen"
modprobe w1-gpio pullup=1
modprobe w1-therm

echo "-----------------------------------"

echo "Einstellungen werden geladen:"

read_dom () {
    local IFS=\>
    read -d \< ENTITY CONTENT
}

while read_dom; do
  if [[ $ENTITY == "1wire_gpio" ]] ; then
    echo "1wire_gpio=$CONTENT"
    wire_gpio=$CONTENT
    echo "-----------------------------------"
  fi
  if [[ $ENTITY == "relais" ]] ; then
    echo "Definiere gpio$CONTENT"
    echo $CONTENT > /sys/class/gpio/export
    sleep 2s
    echo "Setze direction auf out fuer gpio$CONTENT"
    echo "out" > /sys/class/gpio/gpio$CONTENT/direction
  fi
done < Konfiguration.xml

echo "-----------------------------------"

i=1
beschrieben=false
while IFS='' read -r line || [[ -n "$line" ]]; do
  if [[ $line == dtoverlay=w1-gpio* ]] ; then
    beschrieben=true
    echo "Beschreibe /boot/config.txt mit fuer 1-wire auf gpio "$wire_gpio
    sed -i $i"s/.*/dtoverlay=w1-gpio,gpiopin="$wire_gpio",pullup=on/" "/boot/config.txt"
  fi
  ((i++))
done < "/boot/config.txt"

if [[ $beschrieben == false ]] ; then
  echo "Beschreibe /boot/config.txt mit fuer 1-wire auf gpio "$wire_gpio
  echo "dtoverlay=w1-gpio,gpiopin="$wire_gpio",pullup=on" >> "/boot/config.txt"
fi
