// clients state

var clients = {};

function get_client(name) {
  if( ! ( name in clients ) ) {
    clients[name] =  {
      name     : name,
      connected: false,
      state    : {},
      queue    : []
    };
  }
  return clients[name];
}

function init_state(state) {
  state.clients.forEach(update_state);
  console.log("TODO: pending registrations", state.registrations);
}

function update_state(client) {
  get_client(client.name).connected = client.connected;
  get_client(client.name).state     = client.state;
  get_client(client.name).queue     = client.queue;    
}
