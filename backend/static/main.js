var store = new Vuex.Store({
  state: {
    properties : {
      prop1: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        data: [ 40, 39, 10, 40, 39, 80, 40 ],
        color: "#0567BA",
        title: 'Property 1',
        flex: 6,
        height: 200
      },
      prop2: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        data: [ 40, 39, 10, 40, 39, 80, 40 ],
        color: "#ff0000",
        title: 'Property 2',
        flex: 6,
        height: 200
      }
    },
    clients: [],
    services: [ 'Client' ],
    setup: {
      status: null
    },
    users: []
  },
  mutations: {
    updateProperty: function(state, update) {
      state.properties[update.id].labels = update.labels;
      state.properties[update.id].data   = update.data;
    },
    upsertClient: function(state, client) {
      // find current (if any)
      var current = state.clients.find(function(element) {
        return element._id == client._id;
      });
      // update or create current
      if(current) {
        for(var k in client) {
          current[k] = client[k];
        }
      } else {
        current = client;
      }
      // replace current (if any)
      state.clients = state.clients.filter(function(item) {
        return item._id != client._id;
      });
      // and add (new) current
      state.clients.push(current);
    },
    registerService: function(state, service) {
      state.services.push(service);
    },
    updateStatus: function(state, status) {
      state.setup.status = status;
    },
    updateUsers: function(state, users) {
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
    removeUser: function(state, user) {
      state.users = state.users.filter(function(item) {
        return item._id != user._id;
      });      
    }
  },
  getters: {
    groups: function(state) {
      return function() {
        var groups = {};
        for(var c in state.clients) {
          var client = state.clients[c];
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
    propertyData: function(state) {
      return function(id) {
        return state.properties[id].data;
      }
    },
    propertyLabels: function(state) {
      return function(id) {
        return state.properties[id].labels;
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
    }
  }
});

// Routes

var routes = [
  { path: '/dashboard', component: Dashboard },
  { path: '/client',    component: Client    },
  { path: "/user",      component: User      },
  { path: "/user/:id",  component: User      },
  { path: "/setup",     component: Setup     }
];

var router = new VueRouter({
  routes: routes,
  mode  : 'history'
});

var app = new Vue({
  el: "#app",
  delimiters: ['${', '}'],
  router: router,
  data: {
    drawer: null,
    sections: [
      { icon: 'home',      text: 'Home',      path: "/"          },
      { icon: 'dashboard', text: 'Dashboard', path: "/dashboard" },
      { icon: 'person',    text: 'Users',     path: "/user"      },
      { icon: 'build',     text: 'Setup',     path: "/setup"     }
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
      store.commit("registerService", service);
    },
    updateStatus: function(status) {
      store.commit("updateStatus", status);
    },
    updateUsers: function(users) {
      store.commit("updateUsers", users);
    }
  }
}).$mount('#app');

// app.fixVuetifyCSS();
