var Setup = {
  template: `
  <div>
    <h1>Status</h1>
    <div v-if="status()" v-html="status()"></div>
    <div v-else>loading setup status...</div>
  </div>
`,
  methods: {
    status : function() {
      return store.getters.setupStatus();
    }
  },
  created: function() {
    $.get( "/api/status", function( value ) {
      app.updateStatus(syntaxHighlight(JSON.stringify(value, null, 2)));
    });    
  }
};
