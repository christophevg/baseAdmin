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
    connected:   false,
    initialized: false,
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
    }
  }
}).$mount('#app');

app.fixVuetifyCSS();
