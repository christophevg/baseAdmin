var store = new Vuex.Store({
  state: {
    clients: {
      loading: false,
      loaded: false,
      data: []
    },
    groups: {
      loaded: false,
      data: {}
    },
    masters: {
      initialized: false,
      data: []
    },
    registrations: {
      initialized: false,
      data: []
    },
    clientComponents: {
      client : [],
      group  : []
    },
    messages: [],
    users: [],
    version: "{{ app.version }}",
    provision: {{ provision }}
  },
  mutations: {
    client: function(state, client) {
      var current = state.clients.data.find(function(element) {
        return element.name == client.name;
      });
      // update or create current
      if(current) {
        current["loaded"] = true;
        for(var k in client) {
          if( ! (k in current) ) {
            Vue.set(current, k, client[k]);
          } else {
            current[k] = client[k];
          }
        }
      } else {
        state.clients.data.push(client);
      }
    },
    queued: function(state, client) {
      var current = state.clients.data.find(function(element) {
        return element.name == client.name;
      });
      if(current) {
        if( ! ("queue" in current)) {
          Vue.set(current, "queue", []);
        }
        current.queue.push(client.payload);
      } else {
        console.log("QUEUED SOMETHING ON UNKNOWN CLIENT ???????");
      }
    },
    releaseClient: function(state, name) {
      state.clients.data = state.clients.data.filter(function(client) {
        return client.name != name;
      });
    },
    clients: function(state, clients) {
      state.clients.data = clients;
    },
    groups: function(state, groups) {
      state.groups.data = groups;
      state.groups.loaded = true;
    },
    newGroup: function(state, name) {
      if(! (name in state.groups.data) ) {
        Vue.set(state.groups.data, name, []);
      }
    },
    connected: function(state, name) {
      var current = state.clients.data.find(function(element) {
        return element.name == name;
      });
      if( current ) {
        current.connected = true;
      } else {
        console.log("not found");
      }
    },
    disconnected: function(state, name) {
      var current = state.clients.data.find(function(element) {
        return element.name == name;
      });
      if( current ) {
        current.connected = false;
      } else {
        console.log("not found");
      }
    },
    join: function(state, update) {
      if(! (update.group in state.groups.data) ) {
        Vue.set(state.groups.data, update.group, []);
      }
      state.groups.data[update.group].push(update.client);
    },
    leave: function(state, update) {
      state.groups.data[update.group] = state.groups.data[update.group].filter(function(name) {
        return name != update.client;
      });
    },
    registrations: function(state, registrations) {
      state.registrations.data = registrations;
      state.registrations.initialized = true;
    },
    registration: function(state, name) {
      var current = state.registrations.data.find(function(registration) {
        return registration._id == name;
      });
      if( ! current ) {
        state.registrations.data.push({ "_id" : name});
      }
    },
    clearRegistration: function(state, name) {
      state.registrations.data = state.registrations.data.filter(function(registration){
        return registration._id != name;
      });
    },
    clientComponent: function(state, service) {
      state.clientComponents.client.push(service);
    },
    groupComponent: function(state, service) {
      state.clientComponents.group.push(service);
    },
    log: function(state, message) {
      state.messages.unshift(message);
      state.messages = state.messages.slice(0, 250);
    }
  },
  actions: {
  },
  getters: {
    groups_loaded: function(state) {
      return function() {
        return state.groups.loaded;
      }
    },
    groups: function(state) {
      return function() {
        return state.groups.data;
      }
    },
    clients: function(state) {
      return function() {
        return state.clients.data.filter(function(client){
          return !("master" in client) || client.master == null;
        });
      }
    },
    client: function(state) {
      return function(name) {
        return state.clients.data.find(function(client) {
          return client.name == name;
        });
      }
    },
    group: function(state, getters) {
      return function(name) {
        if(name == "all") {
          return getters.clients().filter(function(client){
            return !("location" in client) || ! client.location;
          }).map(function(client){ return client.name; })
            .filter(function(item) { return item; });
        } else {
          return state.groups.data[name];
        }
      }
    },
    groupClients: function(state) {
      return function(name) {
        return this.group(name).map(function(name){
          return store.getters.client(name);
        }).filter(function(item) { return item; });
      }
    },
    masters: function(state, getters) {
      return function() {
        return getters.clients().filter(function(client){
          return ("location" in client) && client.location;
        });
      }
    },
    masterClients: function(state) {
      return function(master) {
        return state.clients.data.filter(function(client){
          return ("master" in client) && client.master == master;
        });
      }
    },
    registrations: function(state) {
      return function() {
        return state.registrations.data;
      }
    },
    logs: function(state) {
      return function() {
        return state.messages;
      }
    }
  }
});
