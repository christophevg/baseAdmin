// clients state

var clients = {};

function get_client(name) {
  if( ! ( name in clients ) ) {
    clients[name] =  {
      name     : name,
      connected: false,
      state    : {},
      queue    : [],
      location : null
    };
  }
  return clients[name];
}

function init_state(state) {
  state.clients.forEach(update_state);
  console.log("TODO: pending registrations", state.registrations);
}

function update_state(state) {
  var client = get_client(state.name)
  client.connected = state.connected;
  client.state     = state.state;
  client.queue     = state.queue;
  client.location  = state.location;
}

function release_client(name) {
  delete clients[name];
}
