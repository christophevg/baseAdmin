var Client = {
  template: `
<div id="dynamic-component-demo" class="demo">
  <h1><v-icon large color="blue darken-2" v-if="$route.params.scope == 'group'">group_work</v-icon> {{ $route.params.id }}</h1>
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
  <div v-else>
    <p v-if="group">
      Groups have no configuration options. Add options using 'app.registerGroupComponents'.
    </p>
    <p v-else>
      Clients have no configuration options. Add options using 'app.registerClientComponents'.
    </p>
  </div>

  <div v-if="group && this.$route.params.id != 'all'">
    <h2>Group Members</h2>
    <div v-if="group.loaded">
      <p style="margin:10px;">

        The following clients are connected to this group. You can add more by
        typing their name at the end of the list, confirming the name with
        'enter'. To have a client leave the group, use the X button next to the
        name of the client.

      </p>
      <div style="margin-top:15px;">
        <v-select v-model="group.clients" chips tags solo append-icon="" @input="joinGroup">
          <template slot="selection" slot-scope="data">
           <v-chip :selected="data.selected" close @input="leaveGroup(data.item._id)">
             <strong>{{ data.item._id }}</strong>&nbsp;
           </v-chip>
          </template>
        </v-select>
      </div>
    </div>
    <div v-else> 
      Hold on, I'm fetching this group for you...
    </div>
  </div>

  <div>
    <h1>Related Activity</h1>
    <v-layout justify-center column>
      <v-card v-for="(message, i) in messages" :key="i">
        <v-card-title>
          <div>
            <v-btn v-if="message.client" depressed small color="primary" @click="gotoClient(message.client)">
              {{ message.client }}
            </v-btn>
            <div v-else class="grey--text">{{ message.topic }}</div>
            <span>{{ message.payload }}</span>
          </div>
        </v-card-title>
      </v-card>
    </v-layout>
  </div>

</div>`,
  data: function() {
    return {
      currentTab: null,
    }
  },
  computed: {
    group: function() {
      if( this.$route.params.scope != "group" ) { return null; }
      return store.getters.group(this.$route.params.id);
    },
    tabs: function() {
      return store.state.clientComponents[this.$route.params.scope];
    },
    currentTabComponent: function () {
      if(! this.currentTab) {
        if(this.tabs.length > 0) {
          this.currentTab = this.tabs[0];
        } else {
          return null;
        }
      }
      return 'Client' + this.currentTab;
    },
    messages : function() {
      var messages = store.getters.messages();
      var related = [];
      for(var i in messages) {
        messages[i]["client"] =
          messages[i].topic[0] == "client" ? messages[i].topic[1] : false;
        if( messages[i].topic[1] == this.$route.params.id ) {
          related.push(messages[i]);
        }
      }
      return related;
    }
  },
  methods: {
    joinGroup: function(data) {
      var client = data[data.length-1];
      var group  = this.$route.params.id;
      MQ.publish("client/" + client + "/groups", {
        "uuid" : uuid(),
        "group" : group,
        "member" : true
      });
      store.dispatch("joinGroup", { group: group, client: client });
    },
    leaveGroup: function(client) {
      var group  = this.$route.params.id;
      MQ.publish("client/" + client + "/groups", {
        "uuid" : uuid(),
        "group" : group,
        "member" : false
      });
      store.dispatch("leaveGroup", { group: group, client: client });
    }
  }
};

// subscribe to store events and handle online/offline events

$( document ).ready(function() {
  store.subscribe( function(mutation, state) {
    if( mutation.type == "newMessage"
     && mutation.payload.topic.length == 2
     && mutation.payload.topic[0] == "client"
     && "status" in mutation.payload.payload )
    {
      client = mutation.payload.payload;
      client["_id"] = mutation.payload.topic[1];
      app.upsertClient(client);
    }
  });
});
