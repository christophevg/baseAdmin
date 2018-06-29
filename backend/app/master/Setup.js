Vue.component( 'ClientSetup', {
  template: `
  <div>
    <div v-if="client.loaded">
      <vue-form-generator :schema="schema" :model="model" :options="formOptions"></vue-form-generator>
      <center>
        <v-btn :loading="saving" @click="updateServices()" class="primary" :disabled="model.isUnchanged">Update</v-btn>
      </center>
    </div>
    <div v-else>
Hold on, I'm loading this client...
    </div>
  </div>
  `,
  computed: {
    client : function() {
      var id = this.$route.params.id;
      var client = store.getters.client(id);
      if(client.loaded) {
        this.setActiveServices(client.services);
      }
      return client;
    }
  },
  methods: {
    setActiveServices: function(services) {
      if(this.initialized) { return; }
      this.initialized = true;
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
      initialized: false,
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
