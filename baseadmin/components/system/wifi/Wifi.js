var MasterWifi = Vue.component( "WifiComponent", {
  template: `
  <div v-if=groups_are_loaded>
    <div v-if="isGroup">
      <b>Note: For groups, no existing networks can be shown. Only adding is possible.</b>
    </div>
  
    <v-card v-for="(network, i) in networks" :key="i">
      <v-card-title>
        <div style="width:100%;">
          <div style="float:right;margin-right:15px;">
            <v-btn color="red" fab small dark @click="removeNetwork(network)">
              <v-icon>delete</v-icon>
            </v-btn>
          </div>
          <span>{{ network }}</span>
        </div>
      </v-card-title>      
    </v-card>

    <center>
      <v-btn @click.stop="addNetworkDialog=true" fab color="primary">
        <v-icon>add</v-icon>
      </v-btn>
    </center>
  
    <v-dialog v-model="addNetworkDialog" max-width="500px">
      <v-card>
        <v-card-title>Add new Wifi network</v-card-title>
        <v-card-text>
          <vue-form-generator :schema="schema" :model="model" :options="formOptions"></vue-form-generator>
        </v-card-text>
        <v-card-actions>
          <v-btn color="secondary" flat @click.stop="closeDialog()">Close</v-btn>
          <v-btn color="primary"   flat @click.stop="addNetwork()">Add</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
  </div>
  `,
  computed: {
    groups_are_loaded: function() {
      return store.getters.groups_loaded();
    },
    isGroup: function() {
      return "scope" in this.$route.params && this.$route.params.scope == "group";
    },
    networks: function() {
      if( "id" in this.$route.params ) {          // group or client
        if(this.$route.params.scope == "group") { //   group
          return [];
        } else {                                  //   client
          var client = store.getters.client(this.$route.params.id);
          try {
            return client.state.current.networks;
          } catch(err) {}
          return [];
        }
      } else {                                    // master
        return store.getters.masterNetworks;
      }
    }
  },
  methods: {
    addNetwork: function() {
      this.saving = true;
      
      var msg = {
        "ssid": this.model.ssid,
        "psk" : this.model.psk
      };
      
      if( "id" in this.$route.params) {
        execute_on(this.$route.params.id, "addNetwork", msg);
      } else {
        var state = this;
        perform("addNetwork", msg, function(result) {
          if("success" in result && result.success) {
            store.commit("newNetwork", msg.ssid);
          } else  {
            app.$notify({
              group: "notifications",
              title: "Failed to add network...",
              text:  "message" in result ? result.message : "unknown reason",
              type:  "warn",
              duration: 10000
            });
            state.addNetworkDialog = false;      
            state.saving            = false;
            state.model.ssid        = "";
            state.model.psk         = "";
            state.model.isUnchanged = true;
          }
        });
      }
      this.addNetworkDialog = false;      
      this.saving            = false;
      this.model.ssid        = "";
      this.model.psk         = "";
      this.model.isUnchanged = true;
    },
    closeDialog: function() {
      this.addNetworkDialog = false;
      this.saving            = false;
      this.model.ssid        = "";
      this.model.psk         = "";
      this.model.isUnchanged = true;
    },
    removeNetwork: function(ssid) {
      var msg = {"ssid" : ssid};
      if( "id" in this.$route.params) {
        execute_on(this.$route.params.id, "removeNetwork", msg);
      } else {
        var state = this;
        perform("removeNetwork", msg, function(result) {
          if("success" in result && result.success) {
            store.commit("removedNetwork", ssid);
          } else  {
            app.$notify({
              group: "notifications",
              title: "Failed to remove network...",
              text:  "message" in result ? result.message : "unknown reason",
              type:  "warn",
              duration: 10000
            });
          }
        });
      }
    }
  },
  data: function() {
    return {
      addNetworkDialog: false,
      saving : false,
      model: {
        isUnchanged: true,
        ssid: "",
        psk : ""
      },
      schema: {
        fields: [
          {
            type: "input",
            inputType: "text",
            label: "Wifi Network Name",
            required: true,
            model: "ssid",
            onChanged: function(model, newVal, oldVal, field) {
              model.isUnchanged = false;
            }
          },
          {
            type: "input",
            inputType: "text",
            label: "Wifi Network Access Password",
            required: true,
            min: 8,
            validator: VueFormGenerator.validators.string,
            model: "psk",
            onChanged: function(model, newVal, oldVal, field) {
              model.isUnchanged = false;
            }
          }
        ]
      },
      formOptions: {
        validateAfterLoad: true,
        validateAfterChanged: true
      }
    }
  }
});

var masterSection = app.sections.find(function(item) {
  return "group" in item && item.group && item.text == "Master";
});
if(! masterSection ) {
  masterSection = {
    group      : true,
    icon       : "home",
    text       : "Master",
    subsections: []
  }
  app.sections.push(masterSection);
}

masterSection.subsections.push({
  icon : "wifi",
  text : "Wifi",
  path : "/wifi"
});

router.addRoutes([{
  path      : "/wifi",
  component : MasterWifi
}]);

store.registerModule("MasterWifi", {
  state: {
    networks: []
  },
  mutations: {
    masterNetworks: function(state, networks) {
      state.networks = networks;
    },
    newNetwork: function(state, network){
      state.networks.push(network);
    },
    removedNetwork: function(state, network) {
      state.networks = state.networks.filter(function(item) {
        return item != network;
      });
    }
  },
  getters: {
    masterNetworks: function(state) {
      return state.networks;
    }
  }
});

state_handlers.push(function(state) {
  store.commit("masterNetworks", state.networks);
});

app.registerClientComponent("Wifi");
app.registerGroupComponent("Wifi");
