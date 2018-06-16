var store = new Vuex.Store({
  state: {
    masters: {
      initialized: false,
      data: []
    },
    messages: [],
    git: "{{ info.git }}"
  },
  mutations: {
    master : function(state, master) {
      var current = state.masters.data.find(function(item) {
        return item._id == master._id;
      });
      if(current) {
        for(var key in master) {
          Vue.set(current, key, master[key]);
        }
      } else {
        state.masters.data.push(master);
      }
    },
    newMessage: function(state, message) {
      state.messages.push(message);
    }
  },
  getters: {
    masters : function(state) {
      return function() {
        if(! state.masters.initialized ) {
          state.masters.initialized = true;
          $.get( "/api/masters", function(masters) {
            console.log(masters);
            for(var index in masters) {
              store.commit("master", masters[index]);
            }
          });
        }
        return state.masters.data;
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
];

// { path: '/master/:id', component: Master    },
// { path: '/client/:id', component: Client    }

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
