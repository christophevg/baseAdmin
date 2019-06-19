var Client = {
  template: `
<div id="dynamic-component-demo" class="demo">
  <h1>
    {{ $route.params.id }}
    <v-icon :color="clientColor" x-large>{{ clientIcon }}</v-icon>
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

  <!--
    <div>
    <h1>Related Activity</h1>
    <v-layout justify-center column>
      <v-card v-for="(message, i) in messages" :key="i">
        <v-card-title>
          <div>
            <div style="display:inline-block;width:155px;text-align:center;margin-right:15px;">{{ message.when }}</div> 
            <span>{{ message.payload }}</span>
          </div>
        </v-card-title>
      </v-card>
    </v-layout>
  </div>
  -->

</div>`,
  data: function() {
    return {
      currentTab: null,
    }
  },
  computed: {
    client: function() {
      return store.getters.client(this.$route.params.id);
    },
    clientColor: function() {
      return this.client && this.client.connected ? "green" : "red";
    },
    clientIcon: function() {
      return this.client && this.client.connected ? "check_circle" : "remove_circle";      
    },
    group: function() {
      if( this.$route.params.scope != "group" ) { return null; }
      return store.getters.group(this.$route.params.id);
    },
    tabs: function() {
      return store.state.clientComponents["client"];
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
      // var messages = store.getters.messages();
      // var related = [];
      // for(var i in messages) {
      //   messages[i]["client"] =
      //     messages[i].topic[0] == "client" ? messages[i].topic[1] : false;
      //   if( messages[i].topic[1] == this.$route.params.id ) {
      //     related.push(messages[i]);
      //   }
      // }
      // return related;
      return [];
    }
  },
  methods: {}
};
