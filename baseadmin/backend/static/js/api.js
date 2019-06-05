// API

function execute(name, cmd, args, schedule) {
  var client = clients[name];
  if(typeof schedule === "undefined") { schedule = ""; }
  var message = {
    "client"   : name,
    "payload": {
      "cmd"      : cmd,
      "args"     : args,
      "schedule" : false
    }
  };

  if(schedule != "") {
    message.payload["schedule"] = 
      moment(schedule, "DD/MM/YY hh:mm:ss").utc().format("HH:mm:ss YYYY-MM-DD");
  }

  log("CMD", message);
  socket.emit("queue", message, function() {
    client.queue.push(message.payload);
    log("QUEUED", client)
  });
  
  return "ok";
}

// accept a client (registration), optionally dispatching it to another master
function accept(name, master) {
  var message = {
    "client" : name,
    "master" : master
  };
  socket.emit("accept", message, function() {
    log("ACCEPTED", name)
  });
}

// release a client
function release(name) {
  socket.emit("release", name, function() {
    release_client(name);
    log("RELEASED", name);
  });
}

// ping a client
function ping(name) {
  socket.emit("ping2", { "client" : name, "start" : Date.now() }, function() {
    log("PING", name);
  });
}
