var Group = {
  template: `
<div class="demo" v-if="groups_are_loaded">
  <h1>
    <v-icon large color="blue darken-2">group_work</v-icon> {{ $route.params.id }}
    <v-icon :color="groupColor" x-large>{{ groupIcon }}</v-icon>
  </h1>
  <hr><br>
  <button
    v-for="tab in tabs"
    v-bind:key="tab"
    v-bind:class="['tab-button', { active: currentTab === tab }]"
    v-on:click="currentTab = tab"
  >{{ tab }}</button>

  <div v-if="tabs.length" class="panel panel-default">
    <div class="panel-body">
      <component v-if="currentTabComponent" v-bind:is="currentTabComponent" class="tab"></component>
    </div>
  </div>

  <div v-if="group">
    <h2>Group Members</h2>
    <div>

      <p style="margin:10px;" v-if="this.$route.params.id != 'all'">
        The following clients are connected to this group. You can add more by
        typing their name at the end of the list, confirming the name with
        'enter'. To have a client leave the group, use the X button next to the
        name of the client.
      </p>
    
      <div style="margin-top:15px;">

        <v-select v-if="this.$route.params.id != 'all'" v-model="groupClients" chips tags solo @input="joinGroup">
          <template slot="selection" slot-scope="data">
           <v-chip v-if="data.item.name" :color="clientColor(data.item)" text-color="white" :selected="data.selected" close @input="leaveGroup(data.item.name)">
             <strong>{{ data.item.name }}</strong>&nbsp;
           </v-chip>
          </template>
        </v-select>

        <v-select v-else v-model="groupClients" chips tags solo>
          <template slot="selection" slot-scope="data">
           <v-chip v-if="data.item.name" :color="clientColor(data.item)" text-color="white" :selected="data.selected">
             <strong>{{ data.item.name }}</strong>&nbsp;
           </v-chip>
          </template>
        </v-select>

      </div>
    </div>
  </div>

</div>`,
  data: function() {
    return {
      currentTab: null,
    }
  },
  computed: {
    groups_are_loaded: function() {
      return store.getters.groups_loaded();
    },
    group: function() {
      return store.getters.group(this.$route.params.id);
    },
    groupClients: {
      get: function() {
        return store.getters.groupClients(this.$route.params.id);
      },
      set: function(newValue) {}  // ignore, we're updated from the "back"
    },
    allClientsConnected: function() {
      var result = this.groupClients.find(function(client){
        return ! client.connected;          
      });
      return typeof result === "undefined";
    },
    groupColor: function() {
      return this.allClientsConnected ? "green" : "red";
    },
    groupIcon: function() {
      return this.allClientsConnected ? "check_circle" : "remove_circle";      
    },
    groupSize: function() {
      return this.groupClients.length;
    },
    tabs: function() {
      return store.state.clientComponents["group"].sort();
    },
    currentTabComponent: function () {
      if(! this.currentTab) {
        if(this.tabs.length > 0) {
          this.currentTab = this.tabs[0];
        } else {
          return null;
        }
      }
      return this.currentTab + "Component";
    }
  },
  methods: {
    clientColor: function(client) {
      return client.connected ? "green" : "red";
    },
    joinGroup: function(data) {
      var client = data[data.length-1];
      if( typeof client !== "string") { return; }
      var group  = this.$route.params.id;
      join(client, group);
    },
    leaveGroup: function(client) {
      var group  = this.$route.params.id;
      leave(client, group);
    }
  }
};
