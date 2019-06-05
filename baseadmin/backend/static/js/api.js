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
  socket.emit("accept", message, function(result) {
    if( result.success ) {
      log("ACCEPTED", name);
    } else {
      log("FAILED", "accept", name, result.message);
    }
  });
}

// release a client
function release(name) {
  socket.emit("release", name, function(result) {
    if( result.success ) {
      release_client(name);
      log("RELEASED", name);
    } else {
      log("FAILED", "release", name, result.message);
    }
  });
}

// ping a client
function ping(name) {
  socket.emit("ping2", { "client" : name, "start" : Date.now() }, function() {
    log("PING", name);
  });
}

// join a client to a group
function join(client, group) {
  socket.emit("join", { "client": client, "group": group }, function(result) {
    if( result.success ) {
      join_group(client, group);
      log("JOINED", client);
    } else {
      log("FAILED", "join", name, result.message);
    }    
  });
}

// leave a client from a group
function leave(client, group) {
  socket.emit("leave", { "client": client, "group": group }, function(result) {
    if( result.success ) {
      leave_group(client, group);
      log("LEFT", client);
    } else {
      log("FAILED", "leave", name, result.message);
    }    
  });
}
