(function() {

  var client = null;
  var clientId = "ws" + Math.random();

  function send(topic, msg) {
    var message = new Paho.MQTT.Message(msg);
    message.destinationName = topic;
    message.qos = 1;
    client.send(message);
  }

  function onConnect() {
    client.subscribe("#");
    send("client/status", clientId + ":online");
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
    if(message.destinationName == "client/status") {
      var parts  = message.payloadString.split(":"),
          client = parts[0],
          online = parts[1] == "online";
      if(online) {
        app.addClient(client);
      } else {
        app.removeClient(client);
      }
    }
  }

  function connect(mqtt) {
    if(! mqtt ) { return; }
    client = new Paho.MQTT.Client(mqtt.hostname, mqtt.port, clientId);

    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    var lwt = new Paho.MQTT.Message( clientId + ":offline");
    lwt.destinationName = "client/status";
    lwt.qos = 1;
    lwt.retained = false;

    var options = {
      useSSL     : mqtt.ssl,
      onSuccess  : onConnect,
      onFailure  : onFailure,
      willMessage: lwt
    }

    if(mqtt.username) {
      options["userName"] = mqtt.username;
      options["password"] = mqtt.password;
    }

    client.connect(options);
  }

  $.get("/api/mq/connection", function(data) {
    connect(data);
  });

  // initialize with clients known at server-side
  $.get("/api/mq/clients", function(clients) {
    console.log(clients);
    for(var i in clients) {
      app.addClient(clients[i]);
    }
  });

})();
