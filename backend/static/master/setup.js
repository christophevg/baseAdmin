var Setup = {
  template: `
  <div>
    <h1>Status</h1>
    <div v-if="status()" v-html="status()"></div>
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
  methods: {
    status : function() {
      return store.getters.setupStatus();
    },
    showDefaultClient: function() {
      this.$router.push("/client/__default__");
    }
  },
  created: function() {
    $.get( "/api/status", function( value ) {
      app.updateStatus(syntaxHighlight(JSON.stringify(value, null, 2)));
    });    
  }
};
