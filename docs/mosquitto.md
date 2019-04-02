# Mosquitto

brew install mosquitto
brew services start mosquitto

```
bind_address 0.0.0.0
port 1883
protocol mqtt

listener 9001 0.0.0.0
protocol websockets
```
