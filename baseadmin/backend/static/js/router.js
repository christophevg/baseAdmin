var routes = [
  { path: '/',            component: Landing   },
  { path: '/dashboard',   component: Dashboard },
  { path: '/master/:id',  component: Master    },
  { path: '/client/:id',  component: Client    },
  { path: '/group/:id',   component: Group     },
  { path: "/user",        component: User      },
  { path: "/user/:id",    component: User      },
  { path: "/log",         component: Log       }
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
    connected:   false,
    initialized: false,
    drawer: null,
    sections: [
      { icon: "dashboard", text: "Dashboard", path: "/dashboard" },
      { icon: "person",    text: "Users",     path: "/user"      },
      { icon: "comment",   text: "Log",       path: "/log"       }
    ]
  },
  methods: {
    fixVuetifyCSS : function() {
      this.$vuetify.theme.info  = '#ffffff';
      this.$vuetify.theme.error = '#ffffff';
    },
    registerClientComponent: function(component) {
      store.commit("clientComponent", component);
    },
    registerGroupComponent: function(component) {
      store.commit("groupComponent", component);
    }
  }
}).$mount('#app');

app.fixVuetifyCSS();
