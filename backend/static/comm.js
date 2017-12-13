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

  function connect(mqtt) {
    if(! mqtt ) { return; }
    var clientId = "ws" + Math.random();
    client = new Paho.MQTT.Client(mqtt.hostname, mqtt.port, clientId);

    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    var options = {
      useSSL   : mqtt.ssl,
      onSuccess: onConnect,
      onFailure: onFailure
    }

    if(mqtt.username) {
      options["userName"] = mqtt.username;
      options["password"] = mqtt.password;
    }

    client.connect(options);
  }

  $.get("/api/mqtt/connection", function(data) {
    connect(data);
  });

})();
