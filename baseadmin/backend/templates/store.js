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
          current[k] = client[k];
        }
      } else {
        state.clients.data.push(client);
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
    }
  },
  actions: {
  },
  getters: {
    client: function(state) {
      return function(name) {
        return state.clients.data.find(function(client) {
          return client.name == name;
        });
      }
    },
    clients: function(state) {
      return function() {
        return state.clients.data;
      }
    },
    groups_loaded: function(state) {
      return function() {
        return state.groups.loaded;
      }
    },
    group: function(state) {
      return function(name) {
        return state.groups.data[name];
      }
    },
    groups: function(state) {
      return function() {
        return state.groups.data;
      }
    },
    masters: function(state) {
      return function() {
        return state.clients.data.filter(function(client){
          return ("location" in client) && client.location;
        });
      }
    },
    registrations: function(state) {
      return function() {
        return state.registrations.data;
      }
    }
  }
});
