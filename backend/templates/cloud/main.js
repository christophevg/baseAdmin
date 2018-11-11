var store = new Vuex.Store({
  state: {
    masters: {
      initialized: false,
      data: []
    },
    messages: [],
    version: "{{ info.version }}"
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

// Routes

var routes = [
  { path: '/',           component: Dashboard },
  { path: '/master/:id', component: Master    }
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
      { icon: "dashboard", text: "Dashboard", path: "/" }
    ]
  },
  methods: {
    fixVuetifyCSS : function() {
      this.$vuetify.theme.info  = '#ffffff';
      this.$vuetify.theme.error = '#ffffff';
    }
  }
}).$mount('#app');

app.fixVuetifyCSS();
