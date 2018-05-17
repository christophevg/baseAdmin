(function() {

  var client = null;
  var clientId = "backend-ui" + Math.random();

  function send(topic, msg) {
    var message = new Paho.MQTT.Message(msg);
    message.destinationName = topic;
    message.qos = 1;
    client.send(message);
  }

  function onConnect() {
    // TODO limit to current scope
    client.subscribe("#");
  }

  function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
      console.log("onConnectionLost", responseObject);
    }
  }

  function onFailure(invocationContext, errorCode, errorMessage) {
    console.log("onFailure", errorMessage);
  }

  function onMessageArrived(message) {
    try {
      var topic = message.destinationName.split("/"),
          event = JSON.parse(message.payloadString);

      if( handle_status_change_events(topic, event) ) { return; }
      console.log("unhandled message", topic, JSON.parse(message.payloadString));

    } catch(err) {
      console.log("Failed to parse JSON message: ", err);
      return;
    }
  }    
    
  function handle_status_change_events(topic, event) {
    // handle status change events
    if( topic.length == 2 && topic[0] == "client" ) {
      var client = topic[1];
      if( "status" in event ) {
        app.upsertClient({
          "_id" : client,
          "status" : event["status"]
        });
        return true;
      }
    }
    return false;
  }

  function handle_stats_update(topic, event) {
    // TODO
    // app.updateProperty()
  }
    
  function connect(mqtt) {
    if(! mqtt ) { return; }
    client = new Paho.MQTT.Client(mqtt.hostname, mqtt.port, clientId);

    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    var options = {
      useSSL     : mqtt.ssl,
      onSuccess  : onConnect,
      onFailure  : onFailure,
      reconnect  : true,
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
  $.get("/api/clients", function(clients) {
    for(var i in clients) {
      app.upsertClient(clients[i]);
    }
  });

})();
