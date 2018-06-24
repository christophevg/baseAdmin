var store = new Vuex.Store({
  state: {
    clients: {
      initialized: false,
      data : []
    },
    services: [],
    clientComponents: [],
    setup: {
      status: null
    },
    users: [],
    messages: [],
    git: "{{ info.git }}"
  },
  mutations: {
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
      state.messages.push(message);
    },

    upsertClient: function(state, client) {
      // find current (if any)
      var current = state.clients.data.find(function(element) {
        return element._id == client._id;
      });
      // update or create current
      if(current) {
        for(var k in client) {
          current[k] = client[k];
        }
      } else {
        state.clients.data.push(client);
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
      state.clientComponents.push(service);
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
          if( ! "config" in current.services[update.service]) {
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
    initClients: function(context) {
      if(! context.state.clients.initialized) {
        context.state.clients.initialized = true;
        // initialize with clients known at server-side
        $.get("/api/clients", function(clients) {
          for(var i in clients) {
            app.upsertClient(clients[i]);
          }
        });
      }
    }
  },
  getters: {
    messages: function(state) {
      return function() {
        return state.messages.slice().reverse();
      }
    },
    groups: function(state) {
      return function() {
        store.dispatch("initClients");
        var groups = {};
        for(var c in state.clients.data) {
          var client = state.clients.data[c];
          if(client._id == "__default__") { continue; }
          var client_groups = client.groups;
          for(var g in client_groups) {
            var group = client_groups[g];
            if(!(group in groups)) {
              groups[group] = {
                name: group,
                excerpt: " ",
                color: "green",
                icon: "check_circle",
                total: 0,
                clients: []
              }
            }
            groups[group].clients.push({
              title: client._id,
              color: client.status == "online" ? "green" : "red"
            });
            groups[group].total++;
            if(client.status != "online") {
              groups[group].color = "red";
              groups[group].icon  = "remove_circle";
            }
          }
        }
        return groups;
      }
    },
    setupStatus: function(state) {
      return function() {
        return state.setup.status;
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
    },
    client: function(state) {
      return function(id) {
        store.dispatch("initClients");
        return state.clients.data.find(function(client) {
          return client._id == id;
        });
      }
    },
    clients: function(state) {
      return function() {
        store.dispatch("initClients");
        return state.clients.data;
      }
    }
  }
});

// Routes

var routes = [
  { path: '/',           component: Dashboard },
  { path: '/client/:id', component: Client    },
  { path: "/user",       component: User      },
  { path: "/user/:id",   component: User      },
  { path: "/setup",      component: Setup     },
  { path: "/log",        component: Log       }
];

var router = new VueRouter({
  routes: routes,
  mode  : 'history'
});

var app = new Vue({
  el: "#app",
  delimiters: ['${', '}'],
  router: router,
  components: {
    multiselect: VueMultiselect.Multiselect
  },
  data: {
    drawer: null,
    sections: [
      { icon: "dashboard", text: "Dashboard", path: "/" },
      { icon: "person",    text: "Users",     path: "/user"      },
      { icon: "build",     text: "Setup",     path: "/setup"     },
      { icon: "comment",   text: "Log",       path: "/log"     }
    ]
  },
  methods: {
    fixVuetifyCSS : function() {
      this.$vuetify.theme.info  = '#ffffff';
      this.$vuetify.theme.error = '#ffffff';
    },
    removeClient: function(client) {
      this.$notify({
        group: "notifications",
        title: "<b>" + client + "</b> Offline",
        text:  "Client <b>" + client + "</b> just went offline.",
        type:  "error",
        duration: 10000
      });
      store.commit("removeClient", client);
    },
    upsertClient: function(client) {
      store.commit("upsertClient", client);
    },
    registerService: function(service) {
      store.commit("service", service);
    },
    registerClientComponent: function(component) {
      store.commit("clientComponent", component);
    },
    updateStatus: function(status) {
      store.commit("updateStatus", status);
    },
    allUsers: function(users) {
      store.commit("allUsers", users);
    }
  }
}).$mount('#app');

app.fixVuetifyCSS();
