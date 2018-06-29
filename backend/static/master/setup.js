var Setup = {
  template: `
  <div>
    <h1>Status</h1>
    <div v-if="setup.loaded" v-html="setup.status"></div>
    <div v-else>loading setup status...</div>
    <h1>Default Client</h1>
    <div>
      Use the button below to create default settings for new clients...<br>
      <v-btn @click="showDefaultClient(); return false;"
             color="primary" class="white--text" round>
        Default Configuration
      </v-btn>
    </div>
  </div>
`,
  computed: {
    setup : function() {
      return store.getters.setup();
    }
  },
  methods: {
    showDefaultClient: function() {
      this.$router.push("/client/__default__");
    }
  }
};

store.registerModule("setup", {
  state: {
    setup: {
      loaded : false,
      status: ""
    }
  },
  mutations: {
    updatedSetup: function(state, update) {
      state.setup.status = update;
      state.setup.loaded = true;
    }
  },
  getters: {
    setup: function(state) {
      return function() {
        if(! state.setup.loaded) {
          $.get( "/api/status", function( value ) {
            store.commit(
              "updatedSetup",
              syntaxHighlight(JSON.stringify(value, null, 2))
            );
          });        
        }
        return state.setup;
      }
    }
  }
});
