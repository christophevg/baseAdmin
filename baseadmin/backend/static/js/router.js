var routes = [
  { path: '/',                         component: Landing   },
  { path: '/dashboard',                component: Dashboard },
  { path: '/master/:id',               component: Master    },
  { path: '/:scope(client|group)/:id', component: Client    },
  { path: "/user",                     component: User      },
  { path: "/user/:id",                 component: User      },
  { path: "/setup",                    component: Setup     },
  { path: "/log",                      component: Log       }
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
      { icon: "dashboard", text: "Dashboard", path: "/dashboard" },
      { icon: "person",    text: "Users",     path: "/user"      },
      { icon: "build",     text: "Setup",     path: "/setup"     },
      { icon: "comment",   text: "Log",       path: "/log"       }
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
    registerGroupComponent: function(component) {
      store.commit("groupComponent", component);
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
