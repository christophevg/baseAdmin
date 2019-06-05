// socket io

var socket;

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
    log("CONNECTED");
    app.connected = true;
  });
  socket.on("disconnect", function() {
    log("DISCONNECTED");
    app.connected = false;
  });

  socket.on("ack", function(state) {
    update_state(state);
    log("ACK", state);
  });

  socket.on("state", function(state) {
    init_state(state)
    log("STATE", state);
  });

  socket.on("performed", function(feedback) {
    update_state(feedback)
    log("PERFORMED", feedback);
  });

  socket.on("connected", function(name){
    get_client(name).connected = true;
    log("CONNECT", name);
  });

  socket.on("disconnected", function(name){
    get_client(name).connected = false;
    log("DISCONNECT", name);
  });


  socket.on("register", function(request){
    log("REGISTER", request);
  });

  socket.on("report", function(data) {
    log("REPORT", data);
  });
  
  socket.on("pong2", function(data) {
    rtt = Date.now() - data["start"];
    log("PONG", data["client"], rtt);
  });
  
  socket.on("location", function(state) {
    update_state(state)
    log("LOCATION", state);
  });
});
