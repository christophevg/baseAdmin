// API

// execute_on is a general purpose function to execute a cmd with arguments and
// optional schedule on a given client or group.
// it returns "ok" when the execution is emitted to the master.
// when the master confirms the message, it is queued and added to the client's
// queue. later an ack from the client will confirm the execution by the client.
// if a schedule was given, the scheduling is acknowledged, else the execution
// itself is acknowledged.

function execute_on(name, cmd, args, schedule) {
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

  log("CMD", name, message);
  socket.emit("queue", message, function() {
    var group = store.getters.group(name);
    if( group ) {
      group.forEach(function(member) {
        store.commit("queued", {"name": member, "payload": message.payload});
        log("QUEUED", member, message.payload);
      });
    } else {
      store.commit("queued", {"name": name, "payload": message.payload});
      log("QUEUED", name, message.payload);
    }
  });
  
  return "ok";
}

// perform is a general purpose function to perform a cmd with arguments on the
// master itself. a callback can be provided to handle the response of the
// master.

function perform(cmd, args, callback) {
  socket.emit(cmd, args, function(result){
    if( typeof result !== 'object' ) {
      result = { "success" : false,  "message" : "unknown reason" };
    }
    if( result.success ) {
      log("MASTER CMD", "master", [cmd, args, "OK"]);
    } else {
      log("MASTER CMD", "master", [cmd, args, "FAILED",result.message]);
    }
    if(typeof callback !== "undefined") { callback(result); }
  });
}

// accept a client (registration), optionally dispatching it to another master
function accept(name, master) {
  var message = {
    "client" : name,
    "master" : master
  };
  socket.emit("accept", message, function(result) {
    if( result.success ) {
      store.commit("client", result.client);
      store.commit("clearRegistration", name);
      log("ACCEPTED", name, result);
    } else {
      log("ACCEPT-FAILED", name, result.message);
    }
  });
}

// release a client
function release(name) {
  socket.emit("release", name, function(result) {
    if( result.success ) {
      store.commit("releaseClient", name);
      log("RELEASED", name);
    } else {
      log("RELEASE-FAILED", name, result.message);
    }
  });
}

// ping a client
function ping(name) {
  var group = store.getters.group(name);
  if(group) {
    group.forEach(function(member) {
      ping_client(member);
    });
  } else {
    ping_client(name);
  }
}

function ping_client(name) {
  var now = Date.now();
  store.commit("client", { name: name, ping_start: now, ping_end: "" } );
  socket.emit("ping2", { "client" : name, "start" : now }, function() {
    log("PING", name, now);
  });  
}

// join a client to a group
function join(client, group) {
  socket.emit("join", { "client": client, "group": group }, function(result) {
    if( result.success ) {
      store.commit("join",  { "client": client, "group": group })
      log("JOINED", client, group);
    } else {
      log("JOIN-FAILED", name, result.message);
      app.$notify({
        group: "notifications",
        title: "Failed to join...",
        text:  "message" in result ? result.message : "unknown reason",
        type:  "warn",
        duration: 10000
      });
    }    
  });
}

// leave a client from a group
function leave(client, group) {
  socket.emit("leave", { "client": client, "group": group }, function(result) {
    if( result.success ) {
      store.commit("leave",  { "client": client, "group": group })
      log("LEFT", client, group);
    } else {
      log("FAILED-LEAVE", name, result.message);
    }    
  });
}
