// socket io

var socket;

var state_handlers = [];

console.log("requesting session token...");
$.get( "/api/session", function socketio_connect(token) {
  console.log("aquired session token", token);
  socket = io(
    "//" + document.domain + ":" + location.port, {
      "transportOptions": {
          "polling": {
            "extraHeaders": {
              "client": "browser",
              "token": token
            }
          }
        }
  });

  socket.on("connect", function() {
    app.connected = true;
    log("CONNECTED");
  });
  socket.on("disconnect", function() {
    app.connected = false;
    log("DISCONNECTED");
  });

  socket.on("ack", function(client) {
    // update_state(client);
    store.commit("client", client);
    log("ACK", client);
  });

  socket.on("state", function(state) {
    // init_state(state);
    store.commit("clients",       state.clients);
    store.commit("groups",        state.groups);
    store.commit("registrations", state.registrations);
    state_handlers.forEach(function(handler){ handler(state); });
    log("STATE", state);
  });

  socket.on("performed", function(client) {
    // update_state(client)
    store.commit("client", client);
    log("PERFORMED", client);
  });

  socket.on("connected", function(name){
    // get_client(name).connected = true;
    store.commit("connected", name);
    log("CONNECT", name);
  });

  socket.on("disconnected", function(name){
    // get_client(name).connected = false;
    store.commit("disconnected", name);
    log("DISCONNECT", name);
  });

  socket.on("register", function(request){
    store.commit("registration", request);
    log("REGISTER", request);
  });

  socket.on("report", function(data) {
    log("REPORT", data);
  });
  
  socket.on("location", function(client) {
    // update_state(client);
    store.commit("client", client);
    log("LOCATION", client);
  });

  socket.on("pong2", function(data) {
    var now = Date.now();
    store.commit("client", { name: data["client"], ping_end: now } );
    log("PONG", data["client"], now - data["start"]);
  });
  
  socket.on("error", function(data) {
    log("ERROR", data);
    app.$notify({
      group: "notifications",
      title: "Error occurred...",
      text:  data,
      type:  "warn",
      duration: 10000
    });
  });
});
