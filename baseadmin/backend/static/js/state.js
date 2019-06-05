// state

var registrations = [];
var clients = {};
var groups  = {};

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
  registrations = state.registrations;
  groups = state.groups;
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

function join_group(client, group) {
  if( ! ( group in groups )) {
    groups[group] = [];
  }
  if( ! ( client in groups[group] ) ) {
    groups[group].push(client);
  }
}

function leave_group(client, group) {
  if( ! ( group in groups )) { return }
  var index = groups[group].indexOf(client);
  if (index !== -1) groups[group].splice(index, 1);
}
