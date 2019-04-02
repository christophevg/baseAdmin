var store = new Vuex.Store({
  state: {
    masters: {
      initialized: false,
      data: []
    },
    messages: [],

    groups: {
      loaded: false,
      data: {}
    },
    clients: {
      loading: false,
      loaded: false,
      data: []
    },
    services: [],
    clientComponents: {
      client : [],
      group  : []
    },
    users: [],
    version: "{{ app.version }}",
    provision: {{ provision }}
  },
  mutations: {
    master : function(state, master) {
      if( ! "clients" in master ) { master["clients"] = []; }
      var current = state.masters.data.find(function(item) {
        return item._id == master._id;
      });
      if(current) {
        for(var key in master) {
          Vue.set(current, key, master[key]);
          Vue.set(current, "state", "loaded");
        }
      } else {
        state.masters.data.push(master);
      }
    },
    deleteMaster: function(state, master) {
      state.masters.data = state.masters.data.filter(function(item) {
        return item._id != master;
      });
    },
    newMessage: function(state, message) {
      state.messages.push(message);
    },
    allUsers: function(state, users) {
      state.users = users;
    },
    newUser: function(state, user) {
      state.users.push(user);
    },
    updatedUser: function(state, user) {
      var current = state.users.find(function(element) {
        return element._id == user._id;
      });
      if(current) {
        for(var k in user) {
          current[k] = user[k];
        }
      } else {
        return;
      }
      state.users = state.users.filter(function(item) {
        return item._id != user._id;
      });
      state.users.push(current);
    },
    removedUser: function(state, user) {
      state.users = state.users.filter(function(item) {
        return item._id != user._id;
      });      
    },
    newMessage: function(state, message) {
      message["when"] = (new Date()).toLocaleString(navigator.language, {hour12:false});
      state.messages.push(message);
    },
    upsertClient: function(state, client) {
      // find current (if any)
      var current = state.clients.data.find(function(element) {
        return element._id == client._id;
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
    joinedGroup: function(state, update) {
      var current = state.clients.data.find(function(element) {
        return element._id == update.client;
      });
      if(current) {
        current.groups.push(update.group)
      } else {
        state.clients.data.push({
          _id: update.client,
          groups: [ update.group ]
        })
      }
    },
    leftGroup: function(state, update) {
      var current = state.clients.data.find(function(element) {
        return element._id == update.client;
      });
      if(current) {
        current.groups = current.groups.filter(function(element) {
          return element != update.group;
        });
      }
    },
    service: function(state, service) {
      state.services.push(service);
    },
    clientServices: function(state, update) {
      // find current (if any)
      var current = state.clients.data.find(function(element) {
        return element._id == update.client;
      });
      if(current) {
        current.services = {}
        for(var s in update.services) {
          current.services[update.services[s].name] = {
            location: update.services[s].location
          }
        }
      }
    },
    clientComponent: function(state, service) {
      state.clientComponents.client.push(service);
    },
    groupComponent: function(state, service) {
      state.clientComponents.group.push(service);
    },
    updateStatus: function(state, status) {
      state.setup.status = status;
    },
    serviceUpdate: function(state, update) {
      // find current (if any)
      var current = state.clients.data.find(function(element) {
        return element._id == update.client;
      });
      if(current) {
        if( update.service in current.services ) {
          if( ! ("config" in current.services[update.service])) {
            current.services[update.service]["config"] = {}
          }
          if( ! current.services[update.service]["config"] ) {
            current.services[update.service]["config"] = {}
          }
          for(var k in update.config) {
            current.services[update.service].config[k] = update.config[k];
          }
        } else {
          console.log("serviceUpdate: unknown service: " + update.service);
        }
      } else {
        console.log("serviceUpdate: unknown client: " + update.client);
      }
    }
  },
  actions: {
    loadMasters: function(context) {
      if(! context.state.masters.initialized ) {
        context.state.masters.initialized = true;
        $.get( "/api/masters", function(masters) {
          for(var index in masters) {
            store.commit("master", masters[index]);
          }
        });
      }
    },
    connect: function(context, connection) {
      // disconnect from previous master (if any)
      for(var index in context.state.masters.data) {
        var master = context.state.masters.data[index];
        master.clients = master.clients.filter(function(item) {
          return item != connection.client;
        });
      }
      // connect to (new) master
      var master = context.state.masters.data.find(function(item) {
        return item._id == connection.master;
      });
      if(master) {
        master.clients.push(connection.client);
      }
    },
    disconnect: function(context, connection) {
      var master = context.state.masters.data.find(function(item) {
        return item._id == connection.master;
      });
      if(master) {
        master.clients = master.clients.filter(function(item) {
          return item != connection.client;
        });
      }      
    },
    initClients: function(context) {
      if(context.state.clients.loading || context.state.clients.loaded) {
        return;
      }
      context.state.clients.loading = true;
      $.get("/api/clients", function(clients) {
        // update client info
        for(var i in clients) {
          clients[i]["loaded"] = true;
          app.upsertClient(clients[i]);
        }
        context.state.clients.loaded = true;
        context.dispatch("rebuildGroups");
      });
    },
    rebuildGroups: function(context) {
      // step 1: clear memberships in all groups
      for(var g in context.state.groups.data) {
        while(context.state.groups.data[g].clients.length > 0) {
          context.state.groups.data[g].clients.pop();
        }
        context.state.groups.data[g].total = 0;
      }
    
      // step 2: add current clients, creating new groups as we go along
      for(var c in context.state.clients.data) {
        var client = context.state.clients.data[c];
        if(client._id == "__default__") { continue; }
        var client_groups = client.groups;
        for(var g in client_groups) {
          var group = client_groups[g];
          if(!(group in context.state.groups.data)) {
            context.state.groups.data[group] = {
              name: group,
              excerpt: " ",
              color: "green",
              icon: "check_circle",
              total: 0,
              clients: []
            }
          }
          context.state.groups.data[group].clients.push({
            title: client._id,
            color: client.status == "online" ? "green" : "red"
          });
          context.state.groups.data[group].total++;
          if(client.status != "online") {
            context.state.groups.data[group].color = "red";
            context.state.groups.data[group].icon  = "remove_circle";
          }
        }
      }
      
      // step 3: prune empty groups
      for(var g in context.state.groups.data) {
        if(context.state.groups.data[g].clients.length < 1) {
          delete context.state.groups.data[g];
        }
      }
      
      context.state.groups.loaded = true;
    },
    joinGroup: function(context, membership) {
      context.commit("joinedGroup", membership);
      context.dispatch("rebuildGroups");
    },
    leaveGroup: function(context, membership) {
      context.commit("leftGroup", membership);
      context.dispatch("rebuildGroups");
    }
  },
  getters: {
    masters : function(state) {
      return function() {
        store.dispatch("loadMasters");
        return state.masters.data;
      } 
    },
    master : function(state) {
      return function(id) {
        store.dispatch("loadMasters");
        var current = state.masters.data.find(function(item) {
          return item._id == id;
        });
        if(! current) {
          current = { "_id": id, state: "loading" };
          store.commit("master", current);
        }
        return current;
      } 
    },
    messages: function(state) {
      return function() {
        return state.messages.slice().reverse();
      }
    },
    groups: function(state) {
      return function() {
        store.dispatch("initClients");
        return state.groups;
      }
    },
    group : function(state) {
      return function(id) {
        store.dispatch("initClients");
        var clients = state.clients.data.filter(function(item) {
          return item.groups && item.groups.indexOf(id) > -1 && item._id != "__default__";
        });
        return { _id: id, clients: clients, loaded: state.clients.loaded };
      } 
    },
    clients: function(state) {
      return function() {
        store.dispatch("initClients");
        return state.clients.data;
      }
    },
    client: function(state) {
      return function(id) {
        store.dispatch("initClients");
        var client = state.clients.data.find(function(client) {
          return client._id == id;
        });
        if(! client) {
          client = { _id : id, loaded: false };
          store.commit("upsertClient", client);
        }
        return client;
      }
    },
    users: function(state) {
      return function() {
        var sorted = [...state.users].sort(function(a,b){
          if(a.name > b.name) { return 1; }
          if(a.name < b.name) { return -1; }
          return 0;
        });
        return sorted;
      }
    },
    user: function(state) {
      return function(id) {
        return state.users.find(function(user) {
          return user._id == id;
        })
      }
    }
  }
});

// subscribe to store events and handle online/offline events

$( document ).ready(function() {
  store.subscribe( function(mutation, state) {
    if( mutation.type == "newMessage"
     && mutation.payload.topic.length == 2
     && mutation.payload.topic[0] == "master" )
    {
      store.commit("master", mutation.payload.payload);
    }
  });
});

