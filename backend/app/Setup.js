Vue.component( 'ClientSetup', {
  template: `
  <div>
    <vue-form-generator :schema="schema" :model="model" :options="formOptions"></vue-form-generator>
    <center>
      <v-btn :loading="saving" @click="updateClient()" class="primary" :disabled="model.isUnchanged">Update</v-btn>
    </center>
  </div>
  `,
  created: function() {
    var id = this.$route.params.id;
    var client = store.getters.client(id);
    if( client ) {
      this.setActiveServices(client.services);
    } else {
      var self = this;
      $.get( "/api/client/" + id, function(client) {
        app.upsertClient(client);
        self.setActiveServices(store.getters.client(id).services);
      });
    }
  },
  methods: {
    setActiveServices: function(services) {
      for(var service in services) {
        this.model.services.push({
          name: service,
          location: services[service].location
        });
      }
    },
    updateClient: function() {
      this.saving = true;
      var id = this.$route.params.id;
      var current = store.getters.client(id).services;
      var self = this;
      // TODO
      // POST new services
      // DELETE deprecated services
      this.saving = false;
      this.model.isUnchanged = true;
    }
  },
  data: function() {
    return {
      saving : false,
      model: {
        isUnchanged: true,
        services: []
      },
      schema: {
        fields: [{
          type:   "vueMultiSelect",    
          model:  "services",
          label:  "Services",
          selectOptions: {
            multiple:      true,
            key:           "name",
            label:         "name",
            trackBy:       "name",
            searchable:    false,
            clearOnSelect: false,
            closeOnSelect: false,
          },
          onChanged: function(model, newVal, oldVal, field) {
            model.isUnchanged = false;
          },  
          values: store.state.services
        }]
      },
      formOptions: {
        validateAfterLoad: true,
        validateAfterChanged: true
      }
    }
  }
});

app.registerClientComponent("Setup");
