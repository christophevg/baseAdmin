function byName(a, b) {
  if( a.name < b.name ) {
    return -1;
  }
  if( a.name > b.name ){
    return 1;
  }
  return 0;
}

var Dashboard = {
  template : `
<div>
  <v-layout justify-center column v-if="groups_are_loaded">

    <v-card v-for="(registration, i) in registrations" :key="i">
      <v-card-title>
        <div style="width:100%;">
          <div style="float:left;margin-right:15px;">
            <v-btn color="green" fab small dark @click.stop="showAcceptRegistrationDialog(registration._id)">
              <v-icon>add_circle_outline</v-icon>
            </v-btn>
          </div>
          <!--<div style="float:right;margin-right:15px;">
            <v-btn color="red" fab small dark @click="rejectRegistration(registration._id)">
              <v-icon>delete</v-icon>
            </v-btn>
          </div>-->
          <span><b>Registration request:</b><br>{{ registration._id }}</span><br>
        </div>
      </v-card-title>      
    </v-card>
    
    <v-card v-for="(master, i) in masters" :key="i">
      <v-card-title>
        <div style="width:100%;">
          <div style="float:left;margin-right:15px;">
            <v-btn color="primary" fab small dark @click="editMaster(master.name)">
              <v-icon>edit</v-icon>
            </v-btn>
            <v-btn :color="clientColor(master)" fab small dark @click="visitMaster(master.location)">
              <v-icon>link</v-icon>
            </v-btn>
          </div>
          <div style="float:right;margin-right:15px;">
            <v-btn color="red" fab small dark @click="deleteMaster(master.name)">
              <v-icon>delete</v-icon>
            </v-btn>
          </div>
          <span>{{ master.name }} @ {{ master.location }}</span><br>
          <span class="grey--text">last update: {{ master.modified | formatDate }}</span>
        </div>
      </v-card-title>
    </v-card>
    
    <v-expansion-panel popout>
  
      <!-- ALL group -->
  
      <v-expansion-panel-content hide-actions>
        <v-layout slot="header" align-center row spacer>
          <v-flex xs4 sm2 md1>
            <v-avatar slot="activator" size="36px">
              <v-icon :color="groupColor('all')" x-large>{{ groupIcon("all") }}</v-icon>
            </v-avatar>
          </v-flex>
          <v-flex sm5 md3 hidden-xs-only>
            <strong>all</strong>
            <span class="grey--text">&nbsp;({{ groupSize("all") }})</span>
          </v-flex>
        </v-layout>

        <div style="float:left;margin-left:15px;">
          <v-btn color="primary" fab small dark @click="editGroup('all')">
            <v-icon>edit</v-icon>
          </v-btn>
        </div>

        <div style="margin-left: 25px;margin-bottom:10px;margin-right: 25px;">
          <v-layout wrap justify-space-around align-center>
            <v-btn v-for="client in groupClients('all')" :key="client.name" @click="showClient(client.name); return false;"
                   :color="clientColor(client)" class="white--text" round>
              {{ client.name }}
            </v-btn>
          </v-layout>
        </div>
      </v-expansion-panel-content>  
  
      <!-- regular groups -->
  
      <v-expansion-panel-content v-for="(group, name) in groups" :key="name" hide-actions>
        <v-layout slot="header" align-center row spacer>
          <v-flex xs4 sm2 md1>
            <v-avatar slot="activator" size="36px">
              <v-icon :color="groupColor(name)" x-large>{{ groupIcon(name) }}</v-icon>
            </v-avatar>
          </v-flex>
          <v-flex sm5 md3 hidden-xs-only>
            <strong v-html="name"></strong>
            <span class="grey--text">&nbsp;({{ groupSize(name) }})</span>
          </v-flex>
        </v-layout>

        <div style="float:left;margin-left:15px;">
          <v-btn color="primary" fab small dark @click="editGroup(name)">
            <v-icon>edit</v-icon>
          </v-btn>
        </div>
            
        <div style="margin-left: 25px;margin-bottom:10px;margin-right: 25px;">
          <v-layout wrap justify-space-around align-center>
            <v-btn v-for="client in groupClients(name)" :key="client.name" @click="showClient(client.name); return false;"
                   :color="clientColor(client)" class="white--text" round>
              {{ client.name }}
            </v-btn>
          </v-layout>
        </div>

      </v-expansion-panel-content>
    </v-expansion-panel>

    <center>
      <v-btn @click.stop="createGroupDialog=true" fab color="primary">
        <v-icon>add</v-icon>
      </v-btn>
    </center>

    <v-dialog v-model="createGroupDialog" max-width="500px">
      <v-card>
        <v-card-title>Create new Group</v-card-title>
        <v-card-text>
          <vue-form-generator :schema="schema" :model="model" :options="formOptions"></vue-form-generator>
        </v-card-text>
        <v-card-actions>
          <v-btn color="secondary" flat @click.stop="createGroupDialog=false">Close</v-btn>
          <v-btn color="primary"   flat @click.stop="createGroup()">Add</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="acceptRegistrationDialog" max-width="500px">
      <v-card>
        <v-card-title>Accept Registration</v-card-title>
        <v-card-text>
          <p>
            Leave blank to accept the registration on this master.
            Provide the name of another master to dispatch the
            registration to that master.
          </p>
          <vue-form-generator :schema="schemaAccept" :model="model" :options="formOptions"></vue-form-generator>
        </v-card-text>
        <v-card-actions>
          <v-btn color="secondary" flat @click.stop="acceptRegistrationDialog=false">Close</v-btn>
          <v-btn color="primary"   flat @click.stop="acceptRegistration()">Accept</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


  </v-layout>
  <div v-else>Hold on,...</div>
</div>
`,
  data: function() {
    return {
      createGroupDialog: false,
      acceptRegistrationDialog: false,
      model: {
        name: "",
        client: "",
        master: ""
      },
      schema: {
        fields: [{
          type: "input",
          inputType: "text",
          label: "name",
          model: "name",
        }]
      },
      schemaAccept: {
        fields: [{
          type: "input",
          inputType: "text",
          label: "master",
          model: "master",
        }]
      },
      formOptions: {
        validateAfterLoad: true,
        validateAfterChanged: true
      }
    }
  },
  computed: {
    groups_are_loaded: function() {
      return store.getters.groups_loaded();
    },
    groups: function() {
      return store.getters.groups();
    },
    masters: function() {
      return store.getters.masters();
    },
    registrations: function() {
      return store.getters.registrations();
    }
  },
  methods: {
    clientColor: function(client) {
      return client.connected ? "green" : "red";
    },
    groupClients: function(name) {
      return store.getters.groupClients(name).concat().sort(byName);
    },
    allClientsConnected: function(name) {
      var result = this.groupClients(name).find(function(client){
        return client && (! client.connected);
      });
      return typeof result === "undefined";
    },
    groupColor: function(name) {
      return this.allClientsConnected(name) ? "green" : "red";
    },
    groupIcon: function(name) {
      return this.allClientsConnected(name) ? "check_circle" : "remove_circle";      
    },
    groupSize: function(name) {
      return this.groupClients(name).length;
    },
    showClient: function(client) {
      this.$router.push('/client/' + client);
    },
    editGroup : function(group) {
      this.$router.push('/group/' + group);
    },
    createGroup: function() {
      if( this.model.name != "" ) {
        store.commit("newGroup", this.model.name);
        this.model.name = "";
      }
      this.createGroupDialog = false;
    },
    editMaster: function(id) {
      this.$router.push("/master/" + id);
    },
    visitMaster: function(location) {
      window.open(location,'_blank');
    },
    deleteMaster: function(name) {
      release(name);
    },
    showAcceptRegistrationDialog: function(client) {
      this.model.client = client;
      this.acceptRegistrationDialog = true;
    },
    acceptRegistration: function() {
      if( this.model.master && this.model.master != "") {
        accept(this.model.client, this.model.master);
      } else if( this.model.client ) {
        accept(this.model.client);        
      }
      this.model.client = "";
      this.model.master = "";
      this.acceptRegistrationDialog = false;
    },
    rejectRegistration: function() {
      console.log("TODO");
    }
  }
};
