(function() {

  var client = null;

  function onConnect() {
    client.subscribe("#");
  }

  function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
      console.log("onConnectionLost:", responseObject.errorMessage);
      setTimeout(function() { client.connect() }, 5000);
    }
  }

  function onFailure(invocationContext, errorCode, errorMessage) {
    console.log(errorMessage);
  }

  function onMessageArrived(message) {
    console.log(message.destinationName, message.payloadString);
    if(message.payloadString == "updateProperty") {
      app.updateProperty(message.destinationName)
    }
  }

  function connect(mqtt_uri) {
    var clientId = "ws" + Math.random();
    client = new Paho.MQTT.Client(
      mqtt_uri.replace("mqtt", "wss").replace("19044", "39044"),
      clientId
    );

    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    client.connect({
      onSuccess: onConnect,
      onFailure: onFailure
    });
  }

  $.get("/api/env/CLOUDMQTT_URL", function(data) {
    connect(data);
  });

})();
