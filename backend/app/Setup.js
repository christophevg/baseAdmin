Vue.component( 'ClientSetup', {
  template: `
  <div>
    <vue-form-generator :schema="schema" :model="model" :options="formOptions"></vue-form-generator>
    <center>
      <v-btn :loading="saving" @click="updateServices()" class="primary" :disabled="model.isUnchanged">Update</v-btn>
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
      this.model.services = [];
      for(var service in services) {
        this.model.services.push({
          name: service,
          location: services[service].location
        });
      }
    },
    updateServices: function() {
      this.saving = true;
      var id = this.$route.params.id;
      var self = this;
      MQ.publish("client/" + id + "/services", {
        "uuid" : uuid(),
        "services" : this.model.services
      });
      // TODO: handle this from own/incoming message?
      store.commit("clientServices", {
        client: id,
        services: this.model.services
      });
      this.setActiveServices(store.getters.client(id).services);
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